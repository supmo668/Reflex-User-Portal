"""
Example state for a long-running task.

This state is used to demonstrate the task API.
Takes no arguments.
"""
import asyncio

import reflex as rx
from ....utils.logger import get_logger

from .base import MonitorState
from ....backend.wrapper.task import monitored_background_task
from ....backend.wrapper.models import TaskStatus, TaskContext

from ....models.admin.admin_config import AdminConfig
logger = get_logger(__name__)

class ExampleTaskState(MonitorState):
    """Example state for a long-running task."""

    @monitored_background_task
    async def task1(self, task: TaskContext):
        """Background task that updates progress.
        Refer to the decorator for more details.

        The 'task' argument is a TaskContext injected by the monitored_background_task decorator.
        Use task.update(...) to update progress/status for the UI.
        """
        logger.info(f"Starting long-running task {task.task_id}")
        for i in range(10):
            # Update progress and status using TaskContext
            await task.update(
                progress=(i + 1) * 10,
                status=TaskStatus.PROCESSING,
            )
            await asyncio.sleep(1)
        logger.info(f"Finished long-running task {task.task_id}")
        return "<My Task Result>"
    
    @monitored_background_task
    async def task2_show_db_config(
        self, task: TaskContext, config_name: str="Default Admin Config"):
        """Background task that fetch and shows a database configuration from AdminConfig.
        """
        logger.info(f"Using database configuration {config_name} for task {task.task_id}")
        with rx.session() as session:
            config = session.exec(
                AdminConfig.select().where(AdminConfig.name == config_name)
            ).first()
            if config:
                logger.info(f"Found AdminConfig: {config.name}")
                return config.configuration  
        return
    
    @rx.event
    async def task2(self, task: TaskContext):
        """Background task that updates progress.
        Refer to the decorator for more details.
        """
        logger.info(f"Starting long-running task2 {task.task_id}")
        for i in range(5):
            logger.info(f"Running long-running task2 {task.task_id} {i}")
            await asyncio.sleep(2)
        logger.info(f"Finished long-running task2 {task.task_id}")