"""
Example state for a long-running task.

This state is used to demonstrate the task API.
Takes multiple arguments
"""

import asyncio
import reflex as rx
from .....utils.logger import get_logger

from ..base import MonitorState
from .....backend.wrapper.task import monitored_background_task, reflex_task, TaskContext
from .....backend.wrapper.models import TaskStatus

from .model import InputArgs

logger = get_logger(__name__)

DEFAULT_TASK_ARGS = InputArgs(name="MATT", age=25)

# Define standalone tasks with @reflex_task decorator
# These functions will be automatically discovered and registered with the MonitorState

@reflex_task
async def task1(task: TaskContext, **kwargs):
    """Background task that updates progress.
    Refer to the decorator for more details.
    """
    logger.info(f"Starting task1 {task.task_id}")
    for i in range(10):
        await task.update(
            progress=(i + 1) * 10,
            status=TaskStatus.PROCESSING,
        )
        await asyncio.sleep(1)
    logger.info(f"Finished task1 {task.task_id}")
    return "<My Task Result>"

# This is Key Example: a task with arguments defined by pydantic model.
# The input is handled automatically and checked for consistency.
# "task_args" should be fixed for signature to be able to identify the input type.
@reflex_task(name="Task With Arguments", description="Task that processes input arguments")
async def task2_with_args(task: TaskContext, task_args: InputArgs = DEFAULT_TASK_ARGS):
    """Background task that updates progress with input arguments."""
    logger.info(f"Starting task2_with_args {task.task_id}")
    
    for i in range(10):
        await task.update(
            progress=(i + 1) * 10,
            status=TaskStatus.PROCESSING,
        )
        await asyncio.sleep(1)
    logger.info(f"Finished task2_with_args {task.task_id}")
    return {**task_args.model_dump()}

# This non-decorated function won't be discovered
async def hidden_task(task: TaskContext):
    """This task won't be discovered because it's not decorated with @reflex_task."""
    logger.info(f"Starting hidden task {task.task_id}")
    await asyncio.sleep(2)
    logger.info(f"Finished hidden task {task.task_id}")
    return "Hidden task completed"

# The state class doesn't need to define the tasks - they will be auto-discovered
class ExampleTaskState2(MonitorState):
    """Example state for a long-running task.
    
    Tasks are defined as standalone functions using @reflex_task decorator
    and automatically discovered when the state is instantiated.
    """
    
    # You can still define tasks directly in the state if you prefer
    @monitored_background_task
    async def class_defined_task(self, task: TaskContext):
        """This task is defined directly in the state class."""
        logger.info(f"Starting class defined task {task.task_id}")
        for i in range(3):
            await task.update(
                progress=(i + 1) * 33,
                status=TaskStatus.PROCESSING,
            )
            await asyncio.sleep(1)
        logger.info(f"Finished class defined task {task.task_id}")
        return "Class defined task completed"