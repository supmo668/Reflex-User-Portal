# Import necessary modules and classes
from fastapi import WebSocket, WebSocketDisconnect, HTTPException, Body
from typing import Optional, Type, Any, Dict
import asyncio

import reflex as rx

from ..states.task.example_task import ExampleTaskState
from ..wrapper.task import TaskStatus

class TaskAPI:
    def __init__(self, app, state_info: Dict[str, Any]):
        self.app = app
        self.state_cls = state_info["cls"]
        self.api_base_path = state_info.get("api_prefix", "/api")
        self.ws_base_path = state_info.get("ws_prefix", "/ws")

    async def start_task(self, client_token: str, session_id: str, task_name: str, parameters: Dict[str, Any] = Body(default=None)):
        """Start a task with optional parameters passed in request body."""
        try:
            # Get state through Reflex's state manager
            monitor_state = await self.app.state_manager.get_state(client_token)
            # monitor_state = await state_manager.get_state(self.state_cls)
            print("Got state:", monitor_state)
            # monitor_state.task_arguments = parameters or {}
            # Get the task method
            task_method = getattr(monitor_state, task_name, None)
            print(f"Running task: {task_name} with parameters: {parameters}")
            if not task_method:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Task {task_name} not found in {self.state_cls.__name__}"
                )
                
            return await self.app.event_namespace.emit_update(
                update=rx.state.StateUpdate(
                    events=rx.event.fix_events([
                        monitor_state.long_running_task], token=client_token),
                ),
                sid=session_id,
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
        await websocket.accept()
        
        try:
            initial_state = await self.get_task_status(client_token, task_id)
            await websocket.send_json({
                "type": "initial_state",
                **initial_state
            })
            
            prev_state = initial_state
            
            while True:
                await asyncio.sleep(0.5)
                try:
                    current_state = await self.get_task_status(client_token)
                    
                    if current_state != prev_state:
                        await websocket.send_json({
                            "type": "state_update",
                            **current_state
                        })
                        prev_state = current_state
                        
                except (KeyError, ValueError) as e:
                    await websocket.send_json({
                        "type": "error", 
                        "message": f"Error updating state: {str(e)}"})
                    
        except WebSocketDisconnect:
            pass
        except asyncio.CancelledError:
            # Handle task cancellation
            await websocket.close()
        except (KeyError, ValueError, HTTPException) as e:
            # Handle known error types
            try:
                await websocket.send_json({
                    "type": "error", 
                    "message": str(e)
                })
            finally:
                await websocket.close()
        except (RuntimeError, ConnectionError) as e:
            # Handle connection/runtime errors
            try:
                await websocket.send_json({
                    "type": "error", 
                    "message": f"Connection error: {str(e)}"
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
        api_base_path = f"{self.api_base_path}/tasks"
        ws_base_path = f"{self.ws_base_path}/tasks"
        # Task management endpoints
        app_instance.api.post(f"{api_base_path}/{{client_token}}/{{session_id}}/start/{{task_name}}")(self.start_task)
        
        # Status endpoints
        app_instance.api.get(f"{api_base_path}/{{client_token}}")(self.get_task_status)
        app_instance.api.get(f"{api_base_path}/{{client_token}}/{{task_id}}")(self.get_task_status)
        
        # Result endpoint
        app_instance.api.get(f"{api_base_path}/{{client_token}}/{{task_id}}/result")(self.get_task_result)

        # WebSocket endpoints - now under /ws/ path
        app_instance.api.websocket(f"{ws_base_path}/{{client_token}}")(self.stream_task_status)
        app_instance.api.websocket(f"{ws_base_path}/{{client_token}}/{{task_id}}")(self.stream_task_status)
        
        


def setup_api(app, state_info: Dict[str, Any]):
    """
    Set up multiple API endpoints for state tasks.
    state_info must contain keys: "cls", "api_prefix", "ws_prefix"
    """
    task_api = TaskAPI(app, state_info)
    task_api.setup_routes(app)
