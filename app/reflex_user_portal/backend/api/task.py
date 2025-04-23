# Import necessary modules and classes
from fastapi import WebSocket, WebSocketDisconnect, HTTPException, Body
from typing import Optional, Type, Any, Dict, Callable
import asyncio
import uuid 
from inspect import signature

from pydantic import BaseModel, ValidationError

import reflex as rx
from .commands import get_route
from ...utils.logger import get_logger
from ...utils.error_handler import (
    TaskError, TaskNotFoundError, InvalidParametersError, create_error_response
)

from ..wrapper.task import TaskStatus

logger = get_logger(__name__)

class TaskAPI:
    def __init__(self, app, state_info: Dict[str, Any]):
        self.app = app
        self.state_cls = state_info["cls"]
        self.api_base_path = state_info.get("api_prefix", "/api")
        self.ws_base_path = state_info.get("ws_prefix", "/ws")

    def _get_input_params(self, task_method, parameters: Dict[str, Any], input_arg_name: str = "task_args") -> Optional[BaseModel]:
        """Get and validate input parameters against the input model if it exists."""
        
        # Get the actual function from EventHandler
        if hasattr(task_method, 'fn'):
            task_method = task_method.fn
            
        sig = signature(task_method)
        logger.debug(f"Method signature: {sig}")
        # 'task' is essential for wrapper to pass 'TaskContext' and must be excluded here for non-detection
        EXCLUDE_PARAM = ["self", "task", "kwargs"]  
        for param in [p for p in sig.parameters.values() if p.name not in EXCLUDE_PARAM]:
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
        return None
    
    async def start_task(self, client_token: str, task_name: str, parameters: Dict[str, Any] = Body(default=None)):
        """
        Start a background task by invoking the task method through a client event.
        Such tasks are not directly accessible from the client and are used for background processing. e.g. ExampleTask.task1
        """
        task_method = getattr(self.state_cls, task_name, None)
        if not task_method:
            return create_error_response(TaskNotFoundError(task_name))
        logger.debug(f"Starting task {task_name} with parameters: {parameters}")
        task_id = str(uuid.uuid4())[:8]
        try:
            validated_params = self._get_input_params(task_method, parameters)
        except ValueError as e:
            return create_error_response(InvalidParametersError(str(e)))
        if isinstance(validated_params, dict) and validated_params.get('error'):
            return validated_params

        async with self.app.state_manager.modify_state(client_token) as state_manager:
            monitor_state = await state_manager.get_state(self.state_cls)
            monitor_state.tasks_argument = {task_id: validated_params or {}}
            await self.app.event_namespace.emit_update(
                update=rx.state.StateUpdate(
                    events=rx.event.fix_events([task_method], token=monitor_state.client_token),
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
                await asyncio.sleep(0.5)
                
        except WebSocketDisconnect:
            logger.info(f"Websocket disconnected for client {client_token}")
        finally:
            await websocket.close()

    def setup_routes(self, app_instance):
        """Set up API endpoints with optional prefix."""
        # Task management endpoints
        app_instance.api.post(
            get_route("start", self.api_base_path, 
                     client_token="{client_token}", 
                     task_name="{task_name}")
        )(self.start_task)
        
        # Status endpoints
        app_instance.api.get(
            get_route("status", self.api_base_path, client_token="{client_token}")
        )(self.get_task_status)
        app_instance.api.get(
            get_route("status_by_id", self.api_base_path, client_token="{client_token}", task_id="{task_id}")
        )(self.get_task_status)
        
        # Result endpoint
        app_instance.api.get(
            get_route("result", self.api_base_path, client_token="{client_token}",
                     task_id="{task_id}")
        )(self.get_task_result)

        # WebSocket endpoints
        app_instance.api.websocket(
            get_route("ws_monitor", self.ws_base_path, client_token="{client_token}")
        )(self.stream_task_status)
        app_instance.api.websocket(
            get_route("ws_task", self.ws_base_path, client_token="{client_token}",
                     task_id="{task_id}")
        )(self.stream_task_status)
        


def setup_api(app, state_info: Dict[str, Any]):
    """
    Set up multiple API endpoints for state tasks.
    state_info must contain keys: "cls", "api_prefix", "ws_prefix"
    """
    task_api = TaskAPI(app, state_info)
    task_api.setup_routes(app)
