import reflex as rx
import functools
import uuid
from typing import Callable, Any
from .models import TaskData, TaskStatus

def monitored_background_task():
    """
    Decorator that wraps rx.event(background=True) to add task monitoring.
    Usage: @monitored_background_task()
    """
    def decorator(func: Callable) -> Callable:
        # Mark the original function
        func.is_monitored_background_task = True
        
        # Create the rx.event wrapper
        event_wrapped = rx.event(background=True)(func)
        
        # Ensure the marker is preserved on the event wrapper
        event_wrapped.is_monitored_background_task = True
        @functools.wraps(event_wrapped)
        async def wrapper(state: rx.State, *args, **kwargs) -> Any:
            """
            Wrrapper function that initializes task data and handles task status updates.
            Args:
                state: The current state of the application
                *args: Positional arguments to pass to the task
                **kwargs: Keyword arguments to pass to the task
            Class Variables created:
                task_id: Unique identifier for the task
                TaskContext: Context manager for updating task status
            """            
            # Pass through the marker to all wrapper layers
            wrapper.is_monitored_background_task = True
            # Generate task ID
            task_id = str(uuid.uuid4())[:8]
            
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
            
            try:
                # Create task context manager for updating task status
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
                
                # Call the original function with task context
                task_ctx = TaskContext(state, task_id)
                result = await event_wrapped(state, task_ctx, *args, **kwargs)
                
                # Mark task as complete with final result
                async with state:
                    state.tasks[task_id].status = TaskStatus.COMPLETED
                    state.tasks[task_id].progress = 100
                    state.tasks[task_id].active = False
                    state.tasks[task_id].result = result
                
                return result
                
            except Exception as e:
                # Handle errors
                async with state:
                    state.tasks[task_id].status = f"{TaskStatus.ERROR}: {str(e)}"
                    state.tasks[task_id].active = False
                    state.tasks[task_id].result = {"error": str(e)}
                raise
        return wrapper
    return decorator
