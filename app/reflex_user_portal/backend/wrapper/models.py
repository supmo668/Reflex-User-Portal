import uuid
from typing import Any
from dataclasses import dataclass, field
import asyncio
import logging

logger = logging.getLogger(__name__)

class TaskContext:
    """Context manager for updating task status in Reflex state."""
    def __init__(self, state, task_id=None):
        self.state = state
        if task_id is None:
            task_id = str(uuid.uuid4()[:8])
        self.task_id = task_id
        
    async def update(self, progress: int, status: str, result: Any = None):
        """Update task progress, status and result in Reflex state"""
        async with self.state:
            self.state.tasks[self.task_id].progress = progress
            self.state.tasks[self.task_id].status = status
            self.state.tasks[self.task_id].active = True
            if result is not None:
                self.state.tasks[self.task_id].result = result


class DirectTaskContext:
    """Task context for direct execution of tasks outside of Reflex state.
    
    This class provides the same interface as TaskContext but works with a global
    task tracker instead of a Reflex state. It's used for executing static methods
    directly through the API.
    """
    def __init__(self, task_id, task_api, global_tracker=None):
        self.task_id = task_id
        self.task_api = task_api
        self.global_tracker = global_tracker
    
    # Implement async context manager protocol
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
        
    async def update(self, progress=None, status=None, result=None):
        """Update task progress, status and result in both global tracker and active_tasks."""
        # Update the global tracker if provided
        if self.global_tracker and hasattr(self.global_tracker, 'tasks'):
            if progress is not None:
                self.global_tracker.tasks[self.task_id]["progress"] = progress
            if status is not None:
                self.global_tracker.tasks[self.task_id]["status"] = status
            if result is not None:
                self.global_tracker.tasks[self.task_id]["result"] = result
        
        # Update the task_api's active_tasks for API endpoints
        if progress is not None:
            self.task_api.active_tasks[self.task_id]["progress"] = progress
        
        if status is not None:
            self.task_api.active_tasks[self.task_id]["status"] = status
        
        if result is not None:
            self.task_api.active_tasks[self.task_id]["result"] = result
        
        logger.debug(f"Task {self.task_id} updated: progress={progress}, status={status}")


class GlobalTaskTracker:
    """A global task tracker that mimics a Reflex state for the TaskContext.
    
    This class provides a simple way to track task progress and status
    without requiring a Reflex state instance.
    """
    def __init__(self):
        self.tasks = {}
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

class TaskStatus:
    PENDING = "PENDING"
    STARTING = "Starting"
    PROCESSING = "Processing"
    COMPLETED = "Completed"
    ERROR = "Error"

# Define TaskData dataclass
@dataclass
class TaskData:
    """Data structure for task information"""
    id: str  # Primary identifier, matches dictionary key
    name: str  # Task name
    status: TaskStatus = TaskStatus.PENDING
    active: bool = False
    progress: int = 0
    result: dict = field(default_factory=dict)
    created_at: float = field(default_factory=lambda: asyncio.get_event_loop().time())
    updated_at: float = field(default_factory=lambda: asyncio.get_event_loop().time())
    
    def to_dict(self) -> dict:
        """Convert task data to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "progress": self.progress,
            "result": self.result,
            "created_at": self.created_at,
        }
