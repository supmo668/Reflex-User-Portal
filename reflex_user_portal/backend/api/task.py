# Import necessary modules and classes
from fastapi import WebSocket, WebSocketDisconnect, HTTPException, Body
from typing import Optional, Type, Any, Dict
import asyncio
import uuid 
from inspect import signature

from pydantic import BaseModel, ValidationError

import reflex as rx
from reflex_user_portal.backend.api.commands import get_route
from reflex_user_portal.utils.logger import get_logger
from reflex_user_portal.utils.error_handler import (
    TaskError, TaskNotFoundError, InvalidParametersError
)

from ..wrapper.task import TaskStatus

logger = get_logger(__name__)

from fastapi import WebSocket, WebSocketDisconnect
import os
from fastapi.websockets import WebSocketState
from typing import Dict, Set

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, client_token: str):
        await websocket.accept()
        if client_token not in self.active_connections:
            self.active_connections[client_token] = set()
        self.active_connections[client_token].add(websocket)

    async def disconnect(self, websocket: WebSocket, client_token: str):
        if client_token in self.active_connections:
            self.active_connections[client_token].remove(websocket)
            if not self.active_connections[client_token]:
                del self.active_connections[client_token]

    async def broadcast(self, message: dict, client_token: str):
        if client_token in self.active_connections:
            dead_connections = set()
            for connection in self.active_connections[client_token]:
                try:
                    if connection.client_state == WebSocketState.CONNECTED:
                        await connection.send_json(message)
                except RuntimeError:
                    dead_connections.add(connection)
            
            # Cleanup dead connections
            for dead in dead_connections:
                await self.disconnect(dead, client_token)

class TaskAPI:
    def __init__(self, app, state_info: Dict[str, Any]):
        self.app = app
        self.state_cls = state_info["cls"]
        self.api_base_path = state_info.get("api_prefix", "/api")
        # Use API_URL env var for WebSocket base path
        self.ws_base_path = state_info.get("ws_prefix", "/ws")
        self.connection_manager = ConnectionManager()

    def _get_input_params(self, task_method, parameters: Dict[str, Any], input_arg_name: str = "task_args") -> Optional[BaseModel]:
        """Get and validate input parameters against the input model if it exists."""
        
        # Get the actual function from EventHandler
        if hasattr(task_method, 'fn'):
            task_method = task_method.fn
            
        sig = signature(task_method)
        logger.debug(f"Method signature: {sig}")
        EXCLUDE_PARAM = ["self", "task", "kwargs"]  # task is given by decorator as TaskContext
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
        task_method = getattr(self.state_cls, task_name, None)
        if not task_method:
            raise TaskNotFoundError(task_name)
        logger.debug(f"Starting task: {task_name} with parameters: {parameters}")
        task_id = str(uuid.uuid4())[:8]
        try:
            validated_params = self._get_input_params(task_method, parameters)
        except ValueError as e:
            raise InvalidParametersError(str(e))

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
                    raise TaskNotFoundError(task_id)
                return monitor_state.tasks[task_id].to_dict()
            
            return {
                "all_tasks": {tid: task.to_dict() for tid, task in monitor_state.tasks.items()}
            }

    
    async def get_task_result(self, client_token: str, task_id: str):
        async with self.app.state_manager.modify_state(client_token) as state_manager:
            monitor_state = await state_manager.get_state(self.state_cls)
            
            if task_id not in monitor_state.tasks:
                raise TaskNotFoundError(task_id)
                
            task = monitor_state.tasks[task_id]
            if task.status != TaskStatus.COMPLETED:
                raise TaskError(
                    f"Task {task_id} not completed. Current status: {task.status}",
                    code=400
                )
            return task.result

    async def stream_task_status(self, websocket: WebSocket, client_token: str, task_id: Optional[str] = None):
        """WebSocket endpoint for streaming real-time task status updates."""
        logger.info(f"New websocket connection for client {client_token}, task {task_id}")
        
        try:
            await self.connection_manager.connect(websocket, client_token)
            prev_state = await self.get_task_status(client_token, task_id)
            prev_state = await websocket.send_json({
                "type": "initial_state",
                **prev_state
            })
            while True:
                try:
                    current_state = await self.get_task_status(client_token, task_id)
                    if current_state != prev_state:
                        # Send updates only if there are changes
                        await self.connection_manager.broadcast({
                            "type": "state_update",
                            "data": current_state
                        }, client_token)

                    # Break if task is completed or errored
                    if task_id and current_state.get("status") in [TaskStatus.COMPLETED, TaskStatus.ERROR]:
                        break
                    await asyncio.sleep(0.5)
                    
                except TaskNotFoundError:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Task {task_id} not found"
                    })
                    break
                    
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for client {client_token}")
        except Exception as e:
            logger.error(f"Error in stream_task_status: {str(e)}")
        finally:
            await self.connection_manager.disconnect(websocket, client_token)

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

        # Remove Socket.IO mount since Reflex handles WebSocket


def setup_api(app, state_info: Dict[str, Any]):
    """
    Set up multiple API endpoints for state tasks.
    state_info must contain keys: "cls", "api_prefix", "ws_prefix"
    """
    task_api = TaskAPI(app, state_info)
    task_api.setup_routes(app)
