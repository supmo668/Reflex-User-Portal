# Import necessary modules and classes
from fastapi import WebSocket, WebSocketDisconnect, HTTPException, Body
from typing import Optional, Type, Any, Dict
import asyncio

import reflex as rx
from ..states.task import MonitorState
from ..wrapper.task import TaskStatus

class TaskAPI:
    def __init__(self, app, state_cls: Type[MonitorState], prefix: str = ""):
        self.app = app
        self.state_cls = state_cls
        self.prefix = prefix.rstrip('/')

    async def start_task(self, client_token: str, task_name: str, parameters: Dict[str, Any] = Body(default=None)):
        """Start a task with optional parameters passed in request body."""
        try:
            async with self.app.state_manager.modify_state(client_token) as state_manager:
                monitor_state = await state_manager.get_state(self.state_cls)
                
                task_method = getattr(monitor_state, task_name, None)
                if not task_method:
                    raise HTTPException(
                        status_code=404, 
                        detail=f"Task {task_name} not found in {self.state_cls.__name__}"
                    )
                
                # Check if method has additional parameters
                if hasattr(task_method, 'additional_params'):
                    required_params = task_method.additional_params
                    type_hints = task_method.type_hints
                    
                    # Validate required parameters are provided
                    if required_params and not parameters:
                        raise HTTPException(
                            status_code=400,
                            detail={
                                "message": "Missing required parameters",
                                "required_params": {
                                    name: str(param_type.__name__) 
                                    for name, param_type in type_hints.items() 
                                    if name in required_params
                                }
                            }
                        )
                    
                    # Pass parameters to the task method
                    return await task_method(**parameters if parameters else {})
                else:
                    # No additional parameters needed
                    return await task_method()

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
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Error starting task: {str(e)}"
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
        except Exception as e:
            try:
                await websocket.send_json({
                    "type": "error", 
                    "message": f"Fatal error: {str(e)}"})
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
        base_path = f"{self.prefix}/tasks"
        
        # Task management endpoints - now accepts POST body
        app_instance.api.post(f"{base_path}/{{client_token}}/start/{{task_name}}")(self.start_task)
        
        # Status endpoints
        app_instance.api.get(f"{base_path}/{{client_token}}")(self.get_task_status)
        app_instance.api.get(f"{base_path}/{{client_token}}/{{task_id}}")(self.get_task_status)
        
        # WebSocket endpoint
        app_instance.api.websocket(f"{base_path}/ws/{{client_token}}/{{task_id}}")(self.stream_task_status)
        
        # Result endpoint
        app_instance.api.get(f"{base_path}/{{client_token}}/{{task_id}}/result")(self.get_task_result)


def setup_api(app, state_cls: Type[MonitorState], prefix: str = ""):
    """
    Set up multiple API endpoints for state tasks.
    """
    task_api = TaskAPI(app, state_cls, prefix)
    task_api.setup_routes(app)

