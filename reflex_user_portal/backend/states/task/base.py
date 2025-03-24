from typing import Dict, List, Optional
import inspect

import reflex as rx
from reflex_user_portal.backend.wrapper.models import TaskStatus, TaskData


class MonitorState(rx.State):
    """Base Monitor State for task tracking."""    
    tasks: Dict[str, TaskData] = {}    
    most_recent_task: Optional[str] = None
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
        """Get all available task functions with their display names.
        Maps function names to their display names based on docstrings or formatted names.
        Only includes methods defined directly in the class (not from base classes).
        """
        task_functions = {}
        
        # Get only methods defined in this specific class (not from base classes)
        class_methods = {
            name: method for name, method in cls.__dict__.items() 
            if callable(method) and not name.startswith('_')
        }
        
        for name, method in class_methods.items():
            # For Reflex EventHandler, we need to check the original function
            if hasattr(method, 'fn'):
                original_func = method.fn
                if hasattr(original_func, 'is_monitored_background_task'):
                    # Get the docstring's first line or use formatted name
                    doc = inspect.getdoc(original_func)
                    if doc:
                        display_name = doc.split('\n')[0].strip()
                    else:
                        display_name = name.replace('_', ' ').title()
                    task_functions[name] = display_name
                    continue

            # For other cases, check through wrapper chain
            current_method = method
            while hasattr(current_method, '__wrapped__'):
                if hasattr(current_method, 'is_monitored_background_task'):
                    # Get the docstring's first line or use formatted name
                    doc = inspect.getdoc(method)
                    if doc:
                        display_name = doc.split('\n')[0].strip()
                    else:
                        display_name = name.replace('_', ' ').title()
                    task_functions[name] = display_name
                    break
                current_method = current_method.__wrapped__
        
        return task_functions
