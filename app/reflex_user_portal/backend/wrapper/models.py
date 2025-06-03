import uuid
import datetime
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

# Configure logger
logger = logging.getLogger(__name__)

class TaskStatus:
    """Task status constants."""
    PENDING = "PENDING"
    STARTING = "Starting"
    PROCESSING = "Processing"
    COMPLETED = "Completed"
    ERROR = "Error"

@dataclass
class TaskData:
    """Data model for tracking task status and results."""
    id: str
    name: str
    status: str = TaskStatus.PENDING
    active: bool = True
    progress: int = 0
    result: Any = None

class TaskContext:
    """Context manager for updating task status in Reflex state."""
    def __init__(self, state, task_id=None):
        self.state = state
        if task_id is None:
            task_id = str(uuid.uuid4()[:8])
        self.task_id = task_id
        self.progress = 0
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
        
    async def update(self, progress=None, status=None, result=None):
        """Update task progress, status and result in Reflex state"""
        async with self.state:
            if progress is not None:
                self.progress = progress
                self.state.tasks[self.task_id].progress = progress
                
            if status is not None:
                self.state.tasks[self.task_id].status = status
                self.state.tasks[self.task_id].active = True
                
            if result is not None:
                self.state.tasks[self.task_id].result = result

class DirectTaskContext:
    """Task context for direct execution of tasks outside of Reflex state.
    
    This class provides the same interface as TaskContext but works directly with
    the TaskAPI to track task status, progress, and results. It's used for executing
    methods decorated with @monitored_background_task directly through the API.
    
    This class maintains its own task history with timestamps for each update,
    making it easier to track task progress and status changes over time.
    """
    def __init__(self, task_id, task_api):
        self.task_id = task_id
        self.task_api = task_api
        self.progress = 0
        self.status = TaskStatus.PENDING
        self.result = None
        self.history = []
        
        # Initialize with first history entry
        self._add_history_entry(progress=0, status=TaskStatus.STARTING)
    
    # Implement async context manager protocol to be compatible with monitored_background_task
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def _add_history_entry(self, progress=None, status=None, message=None, result=None):
        """Add an entry to the task history with the current timestamp."""
        timestamp = datetime.datetime.now().isoformat()
        
        # Only include non-None values in the history entry
        entry = {"timestamp": timestamp}
        if progress is not None:
            entry["progress"] = progress
        if status is not None:
            entry["status"] = status
        if message is not None:
            entry["message"] = message
        if result is not None:
            entry["result"] = result
            
        self.history.append(entry)
        return entry
        
    async def update(self, progress=None, status=None, message=None, result=None):
        """Update task progress, status and result.
        
        Records the update in task history with a timestamp and updates the
        task_api's active_tasks for API endpoints.
        
        Args:
            progress: Optional progress value (0-100)
            status: Optional status string
            message: Optional status message
            result: Optional result data
        """
        # Update local state
        if progress is not None:
            self.progress = progress
        if status is not None:
            self.status = status
        if result is not None:
            self.result = result
            
        # Add to history
        history_entry = self._add_history_entry(progress, status, message, result)
        
        # Update the task_api's active_tasks for API endpoints
        if self.task_id in self.task_api.active_tasks:
            if progress is not None:
                self.task_api.active_tasks[self.task_id]["progress"] = progress
            if status is not None:
                self.task_api.active_tasks[self.task_id]["status"] = status
            if message is not None:
                self.task_api.active_tasks[self.task_id]["message"] = message
            if result is not None:
                self.task_api.active_tasks[self.task_id]["result"] = result
        
        logger.debug(f"Task {self.task_id} updated: progress={progress}, status={status}, message={message}, timestamp={history_entry['timestamp']}")