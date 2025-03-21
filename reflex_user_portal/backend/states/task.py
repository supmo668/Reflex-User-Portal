import reflex as rx
import asyncio
from typing import Dict, List, Any
from reflex_user_portal.backend.wrappers.models import TaskStatus, TaskData
from reflex_user_portal.backend.wrappers.task import monitored_background_task

# Define state
class MonitorState(rx.State):
    """The app state with production-ready task tracking."""    
    # Dictionary to store multiple tasks
    tasks: Dict[str, TaskData] = {}
    @rx.var
    def client_token(self) -> str:
        """Token for client identification."""
        return self.router.session.client_token
    
    @rx.var
    def current_active_tasks(self) -> List[TaskData]:
        """List of currently active tasks, sorted by creation time (newest first)."""
        active_tasks = [
            task for task in self.tasks.values() 
            if task.status in [TaskStatus.STARTING, TaskStatus.PROCESSING]
        ]
        return sorted(active_tasks, key=lambda x: x.created_at, reverse=True)
    @rx.var
    def completed_tasks(self) -> List[TaskData]:
        """List of currently active tasks, sorted by creation time (newest first)."""
        completed_tasks = [
            task for task in self.tasks.values() 
            if task.status in [TaskStatus.FINISHED, TaskStatus.ERROR]
        ]
        return sorted(completed_tasks, key=lambda x: x.created_at, reverse=True)

    # API route handler
    async def api_get_task_status(self, task_id: str) -> dict:
        """Get task status through API."""
        if task_id in self.tasks:
            return self.tasks[task_id].to_dict()
        return {"error": "Task not found"}
        
    @monitored_background_task()
    async def long_running_task(self, task: Any):
        """Background task that updates progress.
        Refer to the decorator for more details.
        """
        for i in range(10):
            await task.update(
                progress=(i + 1) * 10,
                status=TaskStatus.PROCESSING,
            )
            await asyncio.sleep(1)