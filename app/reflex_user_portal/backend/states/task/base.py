from typing import Dict, List, Optional, Union
import inspect
from pydantic import BaseModel
from sqlmodel import select, desc

import reflex as rx
from ....backend.wrapper.models import TaskStatus, TaskData

from ....models.admin.admin_config import AdminConfig
from ....utils.logger import get_logger

logger = get_logger(__name__)

class MonitorState(rx.State):
    """
    Base Monitor State for task tracking.

    Child classes can define background tasks using the @monitored_background_task decorator.
    The decorated task functions will receive a TaskContext instance (commonly named 'task') as their second argument.
    You can call task.update(progress=..., status=...) inside your task function to update the progress and status,
    which will be reflected in the UI and tracked in the MonitorState.tasks dictionary.

    Example usage in a child class (see ExampleTaskState):

        @monitored_background_task
        async def my_task(self, task: TaskContext):
            for i in range(10):
                await task.update(progress=(i+1)*10, status=TaskStatus.PROCESSING)
                await asyncio.sleep(1)
    """
    tasks: Dict[str, TaskData] = {}    
    current_task_function: str = ""
    # Arguments for the current task. Mapping of task ID to its arguments.
    tasks_argument: Dict[str, BaseModel] = {}
    
    # this is for API access (task ID + task arguments)
    enqueued_tasks: Dict[str, dict] = {}
    
    @rx.var
    def client_token(self) -> str:
        """Token for client identification."""
        return self.router.session.client_token
    @rx.var
    def session_id(self) -> str:
        """Session ID for client identification."""
        return self.router.session.session_id
    @rx.var
    def active_tasks(self) -> List[TaskData]:
        """List of currently active tasks, sorted by creation time (newest first)."""
        active_tasks = [
            task for task in self.tasks.values() 
            if task.status in [TaskStatus.STARTING, TaskStatus.PROCESSING]
        ]
        return sorted(active_tasks, key=lambda x: x.created_at, reverse=True)
    @rx.var
    def completed_tasks(self) -> List[TaskData]:
        """List of currently active tasks, sorted by creation time (newest first)."""
        completed_tasks = [
            task for task in self.tasks.values() 
            if task.status in [TaskStatus.COMPLETED, TaskStatus.ERROR]
        ]
        return sorted(completed_tasks, key=lambda x: x.created_at, reverse=True)

    @classmethod
    def get_task_functions(cls) -> Dict[str, str]:
        """
        Get all available task functions with their display names.
        Maps function names to their display names based on docstrings or formatted names.
        Only includes methods defined directly in the class (not from base classes).
        Returns:
            Dictionary mapping: function names -> display names.
        """
        task_functions = {}
        
        # Get only methods defined in this specific class (not from base classes)
        class_methods = {
            name: method for name, method in cls.__dict__.items() 
            if callable(method) and not name.startswith('_')
        }
        
        for name, method in class_methods.items():
            # For Reflex EventHandler, we need to check the original function
            if hasattr(method, 'fn') and hasattr(method.fn, 'is_monitored_background_task'):
                # Get the docstring's first line or use formatted name
                doc = inspect.getdoc(method.fn)
                if doc:
                    display_name = doc.split('\n')[0].strip()
                else:
                    display_name = name.replace('_', ' ').title()
                task_functions[name] = display_name
        if task_functions:
            # Sort task functions by their display names
            task_functions = dict(sorted(task_functions.items(), key=lambda item: item[0]))
        return task_functions
        
    @rx.event
    def change_task_function(self, function_name: str):
        """Change the current task function."""
        if function_name in self.get_task_functions():
            self.current_task_function = function_name
        else:
            raise ValueError(f"Invalid task function. Available functions: {list(self.get_task_functions().keys())}")



class ConfigurableMonitorState(MonitorState):  # Change inheritance to include MonitorState
    """Base state class for task states that need configuration management."""
    # Define "config_name" in subclass
    config_name: str = ""
    # Define "default_config" in subclass
    # default_config: dict = {}  # Must be overridden by subclasses
    
    @rx.var
    def default_config(self) -> Dict[str, Union[str, int, float, bool, None]]:
        return {}
        
    @rx.var
    def config(self) -> Dict[str, Union[str, int, float, bool, None]]:
        """Get the latest configuration from database."""
        if not self.config_name:
            logger.warning("config_name not set in subclass")
            return self.default_config

        try:
            with rx.session() as session:
                # Query for latest version of named config
                config = session.exec(
                    select(AdminConfig)
                    .where(AdminConfig.name == self.config_name)
                    .order_by(desc(AdminConfig.version))
                    .limit(1)
                ).first()
                
                if config:
                    return config.configuration
                    
        except Exception as e:
            logger.error(f"Error fetching configuration: {str(e)}")
            
        return self.default_config

    @classmethod
    def get_config_from_db(cls, config_name: str, default_config: Optional[Dict[str, Union[str, int, float, bool, None]]] = None) -> Dict[str, Union[str, int, float, bool, None]]:
        """Static method to get configuration - maintained for backwards compatibility."""
        try:
            with rx.session() as session:
                config = session.exec(
                    select(AdminConfig)
                    .where(AdminConfig.name == config_name)
                    .order_by(desc(AdminConfig.version))
                    .limit(1)
                ).first()
                
                if config:
                    return config.configuration
                    
        except Exception as e:
            logger.error(f"Error fetching configuration: {str(e)}")
            
        return default_config or {}
