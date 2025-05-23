import reflex as rx
import functools
import uuid
import inspect
from typing import Any, Dict, Optional, Callable, Type
from .models import TaskData, TaskStatus, TaskContext

from ...utils.logger import get_logger

logger = get_logger(__name__)

def reflex_task(func=None, *, name=None, description=None):
    """
    Decorator that marks a function as a task that can be discovered by MonitorState.
    This allows defining task logic outside of state classes.
    
    Usage:
        @reflex_task
        async def my_task(task_ctx, task_args=None):
            # Task implementation
            return result
    
    Args:
        func: The function to decorate
        name: Optional display name for the task
        description: Optional description for the task
    
    Returns:
        The decorated function with metadata attached
    """
    def decorator(func):
        # Add metadata to the function
        func.is_reflex_task = True
        func.task_name = name or func.__name__.replace('_', ' ').title()
        func.task_description = description or (func.__doc__ or "").split('\n')[0].strip()
        return func
        
    # Handle both @reflex_task and @reflex_task() syntax
    if func is None:
        return decorator
    return decorator(func)

def monitored_background_task(func):
    """
    Decorator that wraps rx.event(background=True) to add task monitoring.
    Usage: 
        @monitored_background_task

    The decorated function receives a TaskContext instance as its second argument (commonly named 'task').
    You can call task.update(progress=..., status=...) inside your function to update the task's progress/status,
    which will be reflected in the UI or any monitoring system.
    """
    @rx.event(background=True)
    @functools.wraps(func)
    async def wrapper(state: rx.State, **kwargs) -> Any:
        # Pass through the marker
        wrapper.is_monitored_background_task = True
        # Initialize task
        async with state:
            if getattr(state, "tasks_argument", {}):
                task_id, task_args = state.tasks_argument.popitem()
                kwargs.update({"task_args": task_args} if task_args else task_args)
            else:
                task_id = str(uuid.uuid4())[:8]
            state.tasks[task_id] = TaskData(
                id=task_id,
                name=func.__name__.replace('_', ' ').title(),
                status=TaskStatus.STARTING,
                active=True,
                progress=0,
                result=None
            )
        try:
            # Create task context
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

    func.is_monitored_background_task = True
    wrapper.is_monitored_background_task = True
    return wrapper
