"""
Example state for a long-running task.

This state is used to demonstrate the task API.
Takes multiple arguments
"""

import asyncio
import reflex as rx
from .....utils.logger import get_logger

from ..base import MonitorState
from .....backend.wrapper.task import monitored_background_task, TaskContext
from .....backend.wrapper.models import TaskStatus

from .model import InputArgs

logger = get_logger(__name__)

DEFAULT_TASK_ARGS = InputArgs(name="MATT", age=25)

# The state class with static methods for tasks
class ExampleTaskState2(MonitorState):
    """Example state for a long-running task.
    
    Tasks are defined as static methods using @monitored_background_task
    to ensure proper task monitoring and execution.
    """
    
    @staticmethod
    @monitored_background_task
    async def task1(task, **kwargs):
        """Background task that updates progress.
        Refer to the decorator for more details.
        """
        logger.info(f"Starting task1 with task object type: {type(task)}")
        logger.info(f"Task ID: {task.task_id if hasattr(task, 'task_id') else 'unknown'}")
        logger.info(f"Task attributes: {dir(task)}")
        
        try:
            for i in range(3):  # Reduced to 3 iterations for faster testing
                logger.info(f"Task1 iteration {i+1}/3")
                await task.update(
                    progress=(i + 1) * 33,  # Adjusted for 3 iterations
                    status=TaskStatus.PROCESSING,
                )
                await asyncio.sleep(0.5)  # Reduced sleep time for faster testing
            
            logger.info(f"Finished task1 successfully")
            return "<Task1 Result>"
        except Exception as e:
            logger.error(f"Error in task1: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise
    
    @staticmethod
    @monitored_background_task
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
    
    @monitored_background_task
    async def instance_task(self, task: TaskContext):
        """This task is defined as an instance method in the state class."""
        logger.info(f"Starting instance task {task.task_id}")
        for i in range(3):
            await task.update(
                progress=(i + 1) * 33,
                status=TaskStatus.PROCESSING,
            )
            await asyncio.sleep(1)
        logger.info(f"Finished instance task {task.task_id}")
        return "Instance task completed"