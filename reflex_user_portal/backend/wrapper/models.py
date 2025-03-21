from dataclasses import dataclass, field
import asyncio

class TaskStatus:
    NOT_STARTED = "PENDING"
    STARTING = "Starting"
    PROCESSING = "Processing"
    FINISHED = "Finished"
    ERROR = "Error"

# Define TaskData dataclass
@dataclass
class TaskData:
    """Data structure for task information"""
    id: str  # Primary identifier, matches dictionary key
    status: TaskStatus = TaskStatus.NOT_STARTED
    active: bool = False
    progress: int = 0
    created_at: float = field(default_factory=lambda: asyncio.get_event_loop().time())
    updated_at: float = field(default_factory=lambda: asyncio.get_event_loop().time())
    
    def to_dict(self) -> dict:
        """Convert task data to dictionary"""
        return {
            "id": self.id,
            "status": self.status,
            "progress": self.progress,
            "created_at": self.created_at
        }
