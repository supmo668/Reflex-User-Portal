import reflex as rx
from typing import Dict, Any, Optional
from .logger import get_logger

logger = get_logger(__name__)

class TaskError(Exception):
    def __init__(self, message: str, code: int = 500, data: Optional[Dict] = None):
        self.message = message
        self.code = code
        self.data = data or {}
        super().__init__(message)

class TaskNotFoundError(TaskError):
    def __init__(self, task_id: str):
        super().__init__(f"Task {task_id} not found", code=404)

class InvalidParametersError(TaskError):
    def __init__(self, message: str):
        super().__init__(message, code=400)

def create_error_response(error: Exception) -> Dict[str, Any]:
    if isinstance(error, TaskError):
        return {
            "error": True,
            "code": error.code,
            "message": error.message,
            "data": error.data
        }
    return {
        "error": True,
        "code": 500,
        "message": str(error)
    }

def create_success_response(data: Any = None) -> Dict[str, Any]:
    return {
        "success": True,
        "data": data
    }

def custom_backend_handler(exception: Exception) -> Optional[rx.event.EventSpec]:
    """Backend exception handler for Reflex.
    
    Args:
        exception: The exception that was raised.
        
    Returns:
        EventSpec with error details or None
    """
    logger.error(f"Backend Error: {str(exception)}")
    error_response = create_error_response(exception)
    
    # Return error response that will be sent to frontend
    return rx.window_alert(f"Error: {error_response['message']}")

def custom_frontend_handler(exception: Exception) -> None:
    """Frontend exception handler for Reflex.
    
    Args:
        exception: The exception that was raised.
    """
    logger.error(f"Frontend Error: {str(exception)}")
    # Frontend errors are handled directly in the browser