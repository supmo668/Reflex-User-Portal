import reflex as rx
import functools
import uuid
from typing import Callable, Any
from .models import TaskData, TaskStatus

class TaskContext:
    def __init__(self, state, task_id):
        self.state = state
        self.task_id = task_id
    
    async def update(self, progress: int, status: str, result: Any = None):
        """Update task progress, status and result"""
        async with self.state:
            self.state.tasks[self.task_id].progress = progress
            self.state.tasks[self.task_id].status = status
            self.state.tasks[self.task_id].active = True
            if result is not None:
                self.state.tasks[self.task_id].result = result

def monitored_background_task(func: Callable = None):
    """
    Decorator that wraps rx.event(background=True) to add task monitoring.
    Can be used with or without parentheses.
    Usage: 
        @monitored_background_task
        or
        @monitored_background_task()
    """
    if func is None:
        return monitored_background_task
        
    @rx.event(background=True)
    @functools.wraps(func)
    async def wrapper(state: rx.State, **kwargs) -> Any:
        # Pass through the marker
        wrapper.is_monitored_background_task = True
        if state.task_arguments:
            kwargs.update(state.task_arguments)
        # Generate task ID
        task_id = kwargs.get("task_id", str(uuid.uuid4()))
        
        # Initialize task
        async with state:
            state.tasks[task_id] = TaskData(
                id=task_id,
                name=func.__name__.replace('_', ' ').title(),
                status=TaskStatus.STARTING,
                active=True,
                progress=0,
                result=None
            )
            if hasattr(state, "most_recent_task"):
                state.most_recent_task = task_id
        
        try:
            # Create task context using the outer TaskContext class
            task_ctx = TaskContext(state, task_id)
            result = await func(state, task_ctx, **kwargs)
            
            # Mark task as complete with final result
            async with state:
                state.tasks[task_id].status = TaskStatus.COMPLETED
                state.tasks[task_id].progress = 100
                state.tasks[task_id].active = False
                state.tasks[task_id].result = result
            
        except Exception as e:
            # Handle errors
            async with state:
                state.tasks[task_id].status = f"{TaskStatus.ERROR}: {str(e)}"
                state.tasks[task_id].active = False
                state.tasks[task_id].result = {"error": str(e)}
            raise
    
    # Mark the original function and wrapper
    func.is_monitored_background_task = True
    wrapper.is_monitored_background_task = True
    return wrapper