import asyncio
import reflex as rx
from reflex_user_portal.utils.logger import get_logger

from ..base import MonitorState
from reflex_user_portal.backend.wrapper.task import monitored_background_task, TaskContext
from reflex_user_portal.backend.wrapper.models import TaskStatus

from .model import InputArgs

logger = get_logger(__name__)

DEFAULT_TASK_ARGS = InputArgs(name="MATT", age=25)

class ExampleTaskState2(MonitorState):
    """Example state for a long-running task."""
    @monitored_background_task
    async def task1(self, task: TaskContext, **kwargs):
        """Background task that updates progress.
        Refer to the decorator for more details.
        """
        logger.info(f"Starting longer task {task.task_id}")
        for i in range(10):
            await task.update(
                progress=(i + 1) * 10,
                status=TaskStatus.PROCESSING,
            )
            await asyncio.sleep(1)
        logger.info(f"Finished longer task {task.task_id}")
        return "<My Task Result>"
    
    # This is Key Example: a task with arguments defined by pydantic model. The input is handled by monitored_background_task and checked for consistency.
    # "task_args" should be fixed for signature to be able to identify the input type in the decorator.
    @monitored_background_task
    async def task2_with_args(self, task: TaskContext, task_args: InputArgs = DEFAULT_TASK_ARGS):
        """Background task that updates progress with input arguments."""
        logger.info(f"Starting loaded task {task.task_id}")
        
        for i in range(10):
            await task.update(
                progress=(i + 1) * 10,
                status=TaskStatus.PROCESSING,
            )
            await asyncio.sleep(1)
        logger.info(f"Finished longer task {task.task_id}")
        return {**task_args.model_dump()}
    
    # Example: this task is not discovered because it's not @monitored_background_task    
    @rx.event
    async def long_task(self, task: TaskContext):
        """Background task that updates progress.
        Refer to the decorator for more details.
        """
        logger.info(f"Starting long task {task.task_id}")
        for i in range(5):
            logger.info(f"Running long task {task.task_id} {i}")
            await asyncio.sleep(2)
        logger.info(f"Finished long task {task.task_id}")