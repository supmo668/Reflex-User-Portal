# Import necessary modules and classes
from fastapi import WebSocket,  WebSocket, WebSocketDisconnect, HTTPException
from typing import Optional
import asyncio

from ..states.task import MonitorState
from ..wrapper.task import TaskStatus
from reflex_user_portal.reflex_user_portal import app

# Function for both general task status and specific task status
async def get_task_status(client_token: str, task_id: Optional[str] = None):
    """
    API endpoint to get task status.
    
    Args:
        client_token: The client's session token
        task_id: Optional specific task ID to retrieve
        
    Returns:
        JSON response with task status information
    """
    try:
        async with app.state_manager.modify_state(client_token) as state_manager:
            monitor_state = await state_manager.get_state(MonitorState)
            # state_attrs = dir(monitor_state)
            # print(f"State attributes: {monitor_state}")
        # If a specific task ID is provided, return just that task
        if task_id:
            if task_id in monitor_state.tasks:
                return monitor_state.tasks[task_id].to_dict()
            else:
                raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        
        return {
            "active_tasks": [task.to_dict() for task in monitor_state.current_active_tasks],
            "all_tasks": {tid: task.to_dict() for tid, task in monitor_state.tasks.items()}
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving task status: {str(e)}")

# WebSocket endpoint for real-time task updates
async def stream_task_status(websocket: WebSocket, client_token: str, task_id: Optional[str] = None):
    """WebSocket endpoint for streaming real-time task status updates."""
    await websocket.accept()
    
    try:
        # Send initial state
        initial_state = await get_task_status(client_token, task_id)
        await websocket.send_json({
            "type": "initial_state",
            **initial_state
        })
        
        prev_state = initial_state
        
        # Poll for changes and send updates
        while True:
            await asyncio.sleep(0.5)  # Poll interval
            try:
                current_state = await get_task_status(client_token)
                
                # Only send updates if state has changed
                if current_state != prev_state:
                    await websocket.send_json({
                        "type": "state_update",
                        **current_state
                    })
                    prev_state = current_state
                    
            except Exception as e:
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

async def get_task_result(client_token: str, task_id: str):
    """
    API endpoint to get task result.
    
    Args:
        client_token: The client's session token
        task_id: Task ID to retrieve result for
        
    Returns:
        JSON response with task result
    """
    try:
        async with app.state_manager.modify_state(client_token) as state_manager:
            monitor_state = await state_manager.get_state(MonitorState)
            
            if task_id in monitor_state.tasks:
                task = monitor_state.tasks[task_id]
                if task.status == TaskStatus.FINISHED:
                    return {"result": task.result}
                else:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Task {task_id} not completed. Current status: {task.status}"
                    )
            else:
                raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving task result: {str(e)}")
        
def setup_api(app):
    """Set up API endpoints."""
    # Endpoint to get status of a all or a specific task
    app.api.get("/tasks/{client_token}")(get_task_status)
    app.api.get("/tasks/{client_token}/{task_id}")(get_task_status)
    
    # WebSocket endpoint for real-time updates
    app.api.websocket("/ws/tasks/{client_token}/{task_id}")(stream_task_status)
    
    # Add result endpoint
    app.api.get("/tasks/{client_token}/{task_id}/result")(get_task_result)
