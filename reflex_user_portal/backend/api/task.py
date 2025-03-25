# Import necessary modules and classes
from fastapi import WebSocket, WebSocketDisconnect, HTTPException, Body
from typing import Optional, Type, Any, Dict
import asyncio

import reflex as rx
from reflex_user_portal.backend.api.commands import get_route
from reflex_user_portal.utils.logger import get_logger

from ..wrapper.task import TaskStatus

logger = get_logger("api.task")

class TaskAPI:
    def __init__(self, app, state_info: Dict[str, Any]):
        self.app = app
        self.state_cls = state_info["cls"]
        self.api_base_path = state_info.get("api_prefix", "/api")
        self.ws_base_path = state_info.get("ws_prefix", "/ws")

    async def start_task(self, client_token: str, task_name: str, parameters: Dict[str, Any] = Body(default=None)):
        """Start a task with optional parameters passed in request body."""
        try:
            task_method = getattr(self.state_cls, task_name, None)
            logger.info(f"Running task: {task_name} with parameters: {parameters}")
            if not task_method:
                logger.error(f"Task {task_name} not found in {self.state_cls.__name__}")
                raise HTTPException(
                    status_code=404, 
                    detail=f"Task {task_name} not found in {self.state_cls.__name__}"
                )
            async with self.app.state_manager.modify_state(client_token) as state_manager:
                monitor_state = await state_manager.get_state(self.state_cls)
                return await self.app.event_namespace.emit_update(
                    update=rx.state.StateUpdate(
                        events=rx.event.fix_events([
                            task_method], token=client_token),
                    ),
                    sid=monitor_state.session_id,
                )

        except AttributeError as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Error accessing task method: {str(e)}"
            ) from e
        except ValueError as e:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid parameters for task: {str(e)}"
            ) from e
        except (TypeError, RuntimeError) as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error executing task: {str(e)}"
            ) from e

    async def get_task_status(self, client_token: str, task_id: Optional[str] = None):
        try:
            async with self.app.state_manager.modify_state(client_token) as state_manager:
                monitor_state = await state_manager.get_state(self.state_cls)
                
                if task_id:
                    if task_id in monitor_state.tasks:
                        return monitor_state.tasks[task_id].to_dict()
                    else:
                        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
                
                return {
                    "all_tasks": {tid: task.to_dict() for tid, task in monitor_state.tasks.items()}
                }
                
        except KeyError as e:
            raise HTTPException(status_code=404, detail=f"Task not found: {str(e)}") from e
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid task data: {str(e)}") from e
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving task status: {str(e)}") from e

    async def stream_task_status(self, websocket: WebSocket, client_token: str, task_id: Optional[str] = None): 
        """WebSocket endpoint for streaming real-time task status updates."""
        logger.info(f"New websocket connection for client {client_token}, task {task_id}")
        await websocket.accept()
        
        try:
            # Get initial state
            initial_state = await self.get_task_status(client_token, task_id)       
            prev_state = initial_state
            
            while True:
                await asyncio.sleep(0.5)
                try:
                    # Get current state using same logic as get_task_status
                    current_state = await self.get_task_status(client_token, task_id)
                    # Only send update if state changed
                    if current_state != prev_state:
                        logger.debug(f"State changed for task {task_id}")
                        await websocket.send_json({
                            "type": "state_update",
                            "data": current_state
                        })
                        prev_state = current_state
                        
                except HTTPException as e:
                    logger.error(f"HTTP error in websocket: {e.detail}")
                    # Send error and close if task not found or invalid
                    await websocket.send_json({
                        "type": "error",
                        "status_code": e.status_code,
                        "detail": e.detail
                    })
                    await websocket.close()
                    break
                        
        except WebSocketDisconnect:
            logger.info(f"Websocket disconnected for client {client_token}")
        except asyncio.CancelledError:
            logger.info(f"Websocket cancelled for client {client_token}")
            await websocket.close()
        except Exception as e:
            logger.exception(f"Error in websocket connection: {str(e)}")
            # Handle any other errors
            try:
                await websocket.send_json({
                    "type": "error",
                    "detail": str(e)
                })
            finally:
                await websocket.close()

    async def get_task_result(self, client_token: str, task_id: str):
        """API endpoint to get task result."""
        try:
            async with self.app.state_manager.modify_state(client_token) as state_manager:
                monitor_state = await state_manager.get_state(self.state_cls)
                
                if task_id in monitor_state.tasks:
                    task = monitor_state.tasks[task_id]
                    if task.status == TaskStatus.COMPLETED:
                        return {"result": task.result}
                    else:
                        raise HTTPException(
                            status_code=400, 
                            detail=f"Task {task_id} not completed. Current status: {task.status}"
                        )
                else:
                    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
                    
        except KeyError as e:
            raise HTTPException(status_code=404, detail=f"Task not found: {str(e)}") from e
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid task data: {str(e)}") from e
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving task result: {str(e)}") from e

    def setup_routes(self, app_instance):
        """Set up API endpoints with optional prefix."""
        # Task management endpoints
        app_instance.api.post(
            get_route("start", self.api_base_path, 
                     token="{client_token}", 
                     task_name="{task_name}")
        )(self.start_task)
        
        # Status endpoints
        app_instance.api.get(
            get_route("status", self.api_base_path, token="{client_token}")
        )(self.get_task_status)
        app_instance.api.get(
            get_route("status_by_id", self.api_base_path, token="{client_token}", task_id="{task_id}")
        )(self.get_task_status)
        
        # Result endpoint
        app_instance.api.get(
            get_route("result", self.api_base_path, token="{client_token}",
                     task_id="{task_id}")
        )(self.get_task_result)

        # WebSocket endpoints
        app_instance.api.websocket(
            get_route("ws_monitor", self.ws_base_path, token="{client_token}")
        )(self.stream_task_status)
        app_instance.api.websocket(
            get_route("ws_task", self.ws_base_path, token="{client_token}",
                     task_id="{task_id}")
        )(self.stream_task_status)
        


def setup_api(app, state_info: Dict[str, Any]):
    """
    Set up multiple API endpoints for state tasks.
    state_info must contain keys: "cls", "api_prefix", "ws_prefix"
    """
    task_api = TaskAPI(app, state_info)
    task_api.setup_routes(app)
