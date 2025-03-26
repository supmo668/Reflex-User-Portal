import asyncio

import reflex as rx
from reflex_user_portal.utils.logger import get_logger

from .base import MonitorState
from reflex_user_portal.backend.wrapper.task import monitored_background_task
from reflex_user_portal.backend.wrapper.models import TaskStatus, TaskContext

logger = get_logger(__name__)

class ExampleTaskState(MonitorState):
    """Example state for a long-running task."""
    @monitored_background_task
    async def long_running_task(self, task: TaskContext):
        """Background task that updates progress.
        Refer to the decorator for more details.
        """
        logger.info(f"Starting long-running task {task.task_id}")
        for i in range(10):
            await task.update(
                progress=(i + 1) * 10,
                status=TaskStatus.PROCESSING,
            )
            await asyncio.sleep(1)
        logger.info(f"Finished long-running task {task.task_id}")
        return "<My Task Result>"
    
    @rx.event
    async def long_running_task2(self, task: TaskContext):
        """Background task that updates progress.
        Refer to the decorator for more details.
        """
        logger.info(f"Starting long-running task2 {task.task_id}")
        for i in range(5):
            logger.info(f"Running long-running task2 {task.task_id} {i}")
            await asyncio.sleep(2)
        logger.info(f"Finished long-running task2 {task.task_id}")