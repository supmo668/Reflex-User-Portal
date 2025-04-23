import uuid
from typing import Any
from dataclasses import dataclass, field
import asyncio

class TaskContext:
    """Context manager for updating task status."""
    def __init__(self, state, task_id=None):
        self.state = state
        if task_id is None:
            task_id = str(uuid.uuid4()[:8])
        self.task_id = task_id
    
    async def update(self, progress: int, status: str, result: Any = None):
        """Update task progress, status and result"""
        async with self.state:
            self.state.tasks[self.task_id].progress = progress
            self.state.tasks[self.task_id].status = status
            self.state.tasks[self.task_id].active = True
            if result is not None:
                self.state.tasks[self.task_id].result = result

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
