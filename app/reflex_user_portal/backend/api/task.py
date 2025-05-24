# Import necessary modules and classes
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Body, APIRouter, HTTPException
from typing import Optional, Any, Dict
import asyncio
import inspect
import logging
import re
import uuid
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, ValidationError, create_model
import reflex as rx
from .commands import get_route
from ...utils.logger import get_logger
from ...utils.error_handler import (
    TaskError, TaskNotFoundError, InvalidParametersError, create_error_response
)

from ..wrapper.models import TaskStatus, TaskData

logger = get_logger(__name__)

class TaskAPI:
    """
    Class response for setting up API endpoints for task management.
    state_info:
        cls: State class
        api_prefix: API prefix (contains state name)
        ws_prefix: WebSocket prefix (contains state name)
    """
    def __init__(self, app: rx.App, state_name: str, state_info: Dict[str, Any]):
        self.app = app
        self.state_cls = state_info["cls"]
        self.state_name = state_name
        self.api_base_path = state_info.get("api_prefix", "/api")
        self.ws_base_path = state_info.get("ws_prefix", "/ws")
        self.router = APIRouter(
            prefix=self.api_base_path, 
            tags=[f"Task API - {state_name}"]
        )
        self.ws_router = APIRouter(
            prefix=self.ws_base_path, 
            tags=[f"WebSocket API - {state_name}"]
        )
        self.direct_router = APIRouter(
            prefix=f"{self.api_base_path}", 
            tags=[f"Direct Task API - {state_name}"]
        )
        self.active_tasks = {}
        self.setup_routes()
        # Register routers with the app instance at init
        self.register_routers(app.api_transformer)

    def _get_input_params(self, task_method, parameters: Dict[str, Any], input_arg_name: str = "task_args") -> BaseModel:
        """
        Get and validate input parameters against the input model if it exists.
        Find the argument name `input_arg_name` in the task method signature.
        If the argument is found, validate the parameters against the model type.
        """
        
        # Get the actual function from EventHandler
        if hasattr(task_method, 'fn'):
            task_method = task_method.fn
            
        sig = inspect.signature(task_method)
        logger.debug(f"Method signature: {sig}. Parameters: {sig.parameters}")
        # 'task' is essential for wrapper to pass 'TaskContext' and must be excluded here for non-detection
        EXCLUDE_PARAM = ["self", "task", "kwargs"]  
        params = [p for p in sig.parameters.values() if p.name not in EXCLUDE_PARAM]
        logger.debug(f"Parameters: {params}")
        for param in params:
            logger.debug(f"Checking parameter: {param.name}")
            # Check both task_args and args since Reflex may use either
            if param.name == input_arg_name:
                model_type = param.annotation
                logger.debug(f"Found matching parameter '{param.name}' with type: {model_type}")
                
                if not parameters:
                    raise ValueError(f"Parameters are required for input model '{param.name}' but none were provided.")
                
                if model_type:
                    try:
                        validated = model_type(**parameters)
                        logger.debug(f"Successfully validated parameters: {validated}")
                        return validated
                    except ValidationError as e:
                        raise ValueError(f"Invalid parameters for input model: {str(e)}")
        logger.debug(f"No matching parameter found for '{input_arg_name}' Available parameters: {params}")
        return create_model('EmptyModel', __base__=BaseModel)()

    
    async def start_task(
            self, client_token: str, task_name: str, parameters: Dict[str, Any] = Body(default=None)
        ):
        """
        Start a background task by invoking the task method through a client event.
        Such tasks are not directly accessible from the client and are used for background processing.
        """
        # Get the task method from the state class
        task_method = getattr(self.state_cls, task_name, None)
        if not task_method:
            logger.error(f"Task method {task_name} not found in {self.state_cls.__name__}")
            return create_error_response(TaskNotFoundError(task_name))
            
        logger.debug(f"Starting task {task_name} with parameters: {parameters}")
        task_id = str(uuid.uuid4())[:8]
        
        # Validate parameters
        try:
            validated_params: BaseModel = self._get_input_params(task_method, parameters)
        except ValueError as e:
            logger.error(f"Parameter validation error: {str(e)}")
            return create_error_response(InvalidParametersError(str(e)))
        logger.debug(f"Validated parameters: {validated_params}")
        # Get state and set up task arguments
        async with self.app.state_manager.modify_state(client_token) as state_manager:
            logger.debug(f"Starting task {task_name} ")
            monitor_state = await state_manager.get_state(self.state_cls)
            # parse pydantic model back as dict
            monitor_state.tasks_argument = {task_id: validated_params.model_dump()}
            await self.app.event_namespace.emit_update(
                update=rx.state.StateUpdate(
                    events=rx.event.fix_events(
                        [task_method], token=monitor_state.client_token
                    ),
                ),
                sid=monitor_state.session_id,
            )
        return {"task_id": task_id}
    
    async def get_task_status(self, client_token: str, task_id: Optional[str] = None):
        async with self.app.state_manager.modify_state(client_token) as state_manager:
            monitor_state = await state_manager.get_state(self.state_cls)
            
            if task_id:
                if task_id not in monitor_state.tasks:
                    return create_error_response(TaskNotFoundError(task_id))
                return monitor_state.tasks[task_id].to_dict()
            
            return {
                "all_tasks": {tid: task.to_dict() for tid, task in monitor_state.tasks.items()}
            }

    
    async def get_task_result(self, client_token: str, task_id: str):
        async with self.app.state_manager.modify_state(client_token) as state_manager:
            monitor_state = await state_manager.get_state(self.state_cls)
            
            if task_id not in monitor_state.tasks:
                return create_error_response(TaskNotFoundError(task_id))
                
            task = monitor_state.tasks[task_id]
            if task.status != TaskStatus.COMPLETED:
                return create_error_response(TaskError(
                    f"Task {task_id} not completed. Current status: {task.status}",
                    code=400
                ))
            return task.result

    async def stream_task_status(self, websocket: WebSocket, client_token: str, task_id: Optional[str] = None): 
        """WebSocket endpoint for streaming real-time task status updates."""
        logger.info(f"New websocket connection for client {client_token}, task {task_id}")
        await websocket.accept()
        
        try:
            while True:
                current_state = await self.get_task_status(
                    client_token, task_id
                )
                
                if current_state.get("error"):
                    break
                    
                await websocket.send_json({
                    "type": "state_update",
                    "data": current_state.get("data")
                })
                
                # Check if all tasks are completed
                if task_id and current_state.get("data", {}).get("status") in [TaskStatus.COMPLETED, TaskStatus.ERROR]:
                    break
                    
                await asyncio.sleep(1)
        except WebSocketDisconnect:
            logger.info(f"Websocket disconnected for client {client_token}")
        except Exception as e:
            logger.error(f"Error in WebSocket connection: {str(e)}")
            await websocket.close()
            
    async def run_task_direct(self, task_name: str, parameters: Dict[str, Any] = Body(default=None)):
        """Execute a task directly.
        
        This bypasses the Reflex event system and executes the task method directly.
        Only works with methods decorated with @monitored_background_task in state classes.
        """
        # Get the task method from the state class
        task_method = getattr(self.state_cls, task_name, None)
        if not task_method:
            logger.error(f"Task method {task_name} not found in {self.state_cls.__name__}")
            raise HTTPException(status_code=404, detail=f"Task {task_name} not found")
            
        # Check if the method has the monitored_background_task decorator
        has_monitored_decorator = hasattr(task_method, 'is_monitored_background_task')
        if not has_monitored_decorator:
            logger.error(f"Task method {task_name} is not decorated with @monitored_background_task")
            raise HTTPException(status_code=400, detail=f"Task {task_name} is not decorated with @monitored_background_task")
        
        # Get the original function from the decorated method
        # The monitored_background_task decorator adds a __wrapped__ attribute to the function
        original_func = getattr(task_method, '__wrapped__', task_method)
        logger.debug(f"Original function: {original_func.__name__}")
        
        logger.debug(f"Executing task {task_name} directly with parameters: {parameters}")
        task_id = str(uuid.uuid4())[:8]
        
        # Validate parameters
        try:
            validated_params = self._get_input_params(task_method, parameters)
        except ValueError as e:
            logger.error(f"Parameter validation error: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        
        # Import the DirectTaskContext and GlobalTaskTracker from models.py
        from ..wrapper.models import DirectTaskContext, GlobalTaskTracker
        
        # Create a global task tracker
        global_tracker = GlobalTaskTracker()
        global_tracker.tasks[task_id] = {
            "progress": 0,
            "status": TaskStatus.STARTING,
            "active": True,
            "result": None
        }
        
        # Create the task context using our properly organized classes
        task_context = DirectTaskContext(task_id, self, global_tracker)
        
        # Initialize our active_tasks structure for API endpoints
        self.active_tasks[task_id] = {
            "status": TaskStatus.STARTING,
            "progress": 0,
            "result": None,
            "error": None
        }
        
        # Execute the task in the background
        asyncio.create_task(self._run_task(task_method, task_context, validated_params))
        
        return {"task_id": task_id}
        
    async def _run_task(self, task_method, task_context, params):
        """Run a task in the background and update its status.
        
        This method executes the original (unwrapped) function directly, bypassing the monitored_background_task wrapper.
        """
        task_id = task_context.task_id
        try:
            # Update task status to processing
            self.active_tasks[task_id]["status"] = TaskStatus.PROCESSING
            
            # Get the original function from the decorated method
            # The monitored_background_task decorator adds a __wrapped__ attribute to the function
            original_func = getattr(task_method, '__wrapped__', task_method)
            logger.debug(f"Original function: {original_func.__name__}")
            
            # Execute the original function directly with the task context
            # This bypasses the monitored_background_task wrapper which expects a state parameter
            if hasattr(params, 'model_dump'):
                result = await original_func(task_context, task_args=params)
            else:
                result = await original_func(task_context)
                
            # Update task status to completed
            self.active_tasks[task_id]["status"] = TaskStatus.COMPLETED
            self.active_tasks[task_id]["progress"] = 100
            self.active_tasks[task_id]["result"] = result
            logger.info(f"Task {task_id} completed successfully with result: {result}")
            
        except Exception as e:
            logger.error(f"Error executing task {task_id}: {str(e)}")
            self.active_tasks[task_id]["status"] = TaskStatus.ERROR
            self.active_tasks[task_id]["error"] = str(e)
    
    async def get_direct_task_result(self, task_id: str):
        """Get the result of a directly executed task."""
        if task_id not in self.active_tasks:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
            
        task_status = self.active_tasks[task_id]["status"]
        if task_status != TaskStatus.COMPLETED:
            raise HTTPException(
                status_code=400, 
                detail=f"Task {task_id} not completed. Current status: {task_status}"
            )
            
        return {"result": self.active_tasks[task_id]["result"]}
    
    async def stream_direct_task_status(self, websocket: WebSocket, task_id: str):
        """WebSocket endpoint for streaming real-time status updates for directly executed tasks."""
        logger.info(f"New direct task websocket connection for task {task_id}")
        await websocket.accept()
        
        try:
            if task_id not in self.active_tasks:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Task {task_id} not found"
                })
                await websocket.close()
                return
                
            while True:
                task_info = self.active_tasks[task_id]
                await websocket.send_json({
                    "type": "status_update",
                    "data": {
                        "task_id": task_id,
                        "status": task_info["status"],
                        "progress": task_info["progress"],
                        "result": task_info["result"],
                        "error": task_info["error"]
                    }
                })
                
                # Check if task is completed or errored
                if task_info["status"] in [TaskStatus.COMPLETED, TaskStatus.ERROR]:
                    break
                    
                await asyncio.sleep(1)
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for task {task_id}")
        except Exception as e:
            logger.error(f"Error in direct task WebSocket connection: {str(e)}")
            await websocket.close()

    def setup_routes(self):
        """Set up API endpoints using APIRouter."""
        # Task management endpoints
        self.router.add_api_route(
            get_route("start", task_name="{task_name}"),
            self.start_task,
            methods=["POST"],
            description=f"Start a task for {self.state_name}",
        )
        
        # Status endpoints
        self.router.add_api_route(
            get_route("status"),
            self.get_task_status,
            methods=["GET"],
            description=f"Get all task statuses for {self.state_name}",
        )
        
        self.router.add_api_route(
            get_route("status_by_id"),
            self.get_task_status,
            methods=["GET"],
            description=f"Get task status for {self.state_name}",
        )
        
        # Result endpoint
        self.router.add_api_route(
            get_route("result"),
            self.get_task_result,
            methods=["GET"],
            description=f"Get task result for {self.state_name}",
        )

        # WebSocket endpoints
        self.ws_router.add_api_websocket_route(
            get_route("ws_monitor"),
            self.stream_task_status,
            name=f"Stream all tasks for {self.state_name}",
        )
        
        self.ws_router.add_api_websocket_route(
            get_route("ws_task"),
            self.stream_task_status,
            name=f"Stream specific task for {self.state_name}",
        )
        
        # Direct task execution routes (static methods)
        self.direct_router.add_api_route(
            get_route("direct_start", task_name="{task_name}"),
            self.run_task_direct,
            methods=["POST"],
            description="Execute a task directly using static methods",
        )

        self.direct_router.add_api_route(
            get_route("direct_result"),
            self.get_direct_task_result,
            methods=["GET"],
            description="Get result of a directly executed task",
        )
        
        # WebSocket for direct task status updates
        self.ws_router.add_api_websocket_route(
            get_route("direct_ws"),
            self.stream_direct_task_status,
            name="stream_direct_task_status",
        )

    def register_routers(self, app_instance: FastAPI):
        """Register the API routers with the FastAPI app."""
        app_instance.include_router(self.router)
        app_instance.include_router(self.ws_router)
        app_instance.include_router(self.direct_router)