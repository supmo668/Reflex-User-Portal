import reflex as rx
import functools
import uuid
from typing import Any
from .models import TaskData, TaskStatus, TaskContext

from ...utils.logger import get_logger

logger = get_logger(__name__)

def monitored_background_task(func=None):
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
    
    # Mark both the original function and wrapper
    func.is_monitored_background_task = True
    wrapper.is_monitored_background_task = True
    return wrapper
