from dataclasses import dataclass, field
import asyncio

class TaskStatus:
    NOT_STARTED = "PENDING"
    STARTING = "Starting"
    PROCESSING = "Processing"
    COMPLETED = "COMPLETED"
    ERROR = "Error"

# Define TaskData dataclass
@dataclass
class TaskData:
    """Data structure for task information"""
    id: str  # Primary identifier, matches dictionary key
    name: str  # Task name
    status: TaskStatus = TaskStatus.NOT_STARTED
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
