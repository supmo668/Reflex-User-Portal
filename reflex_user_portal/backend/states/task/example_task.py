import asyncio
from typing import Any
from .base import MonitorState
from reflex_user_portal.backend.wrapper.task import monitored_background_task, TaskContext
from reflex_user_portal.backend.wrapper.models import TaskStatus

class ExampleTaskState(MonitorState):
    """Example state for a long-running task."""
    @monitored_background_task()
    async def long_running_task(self, task: TaskContext):
        """Example background task 1.
        Refer to the decorator for more details.
        """
        for i in range(10):
            await task.update(
                progress=(i + 1) * 10,
                status=TaskStatus.PROCESSING,
            )
            await asyncio.sleep(1)
        return "<My Task Result>"
    
    @monitored_background_task()
    async def long_running_task2(self, task: TaskContext):
        """Example background task 2.
        Refer to the decorator for more details.
        """
        for i in range(5):
            await task.update(
                progress=(i + 1) * 20,
                status=TaskStatus.PROCESSING,
            )
            await asyncio.sleep(2)
        return "<My Task Result2>"