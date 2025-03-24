import os
import importlib
import inspect
from typing import Dict, Type, Callable

import reflex as rx
from .base import MonitorState
from .example_task import ExampleTaskState

def discover_task_states() -> tuple[Dict[str, str], Dict[str, Type[MonitorState]]]:
    """
    Dynamically discover all task state classes in the task module directory.
    Returns:
        state_mappings
    """
    states_dir = os.path.dirname(__file__)
    state_mappings: Dict[str, dict] = {}
    
    # Skip these files when looking for state modules
    skip_files = {'__init__.py', '__pycache__', 'base.py'}
    
    # Scan directory for potential state modules
    for item in os.listdir(states_dir):
        if item in skip_files or not (item.endswith('.py') or os.path.isdir(os.path.join(states_dir, item))):
            continue
            
        module_name = item[:-3] if item.endswith('.py') else item
        try:
            # Import the module using absolute import path
            module_path = f"reflex_user_portal.backend.states.task.{module_name}"
            module = importlib.import_module(module_path)
            
            # Find all classes that inherit from MonitorState
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, MonitorState) and 
                    obj != MonitorState):
                    # Generate API prefix from module and class name
                    state_mappings[obj.__name__] = {
                        "api_prefix": f"/api/tasks/",
                        "module_name": module_name,
                        "cls": obj
                    }
                    
        except ImportError as e:
            print(f"Warning: Could not import module {module_name}: {e}")
            continue
            
    return state_mappings

# Discover all task states
STATE_MAPPINGS = discover_task_states()
ExampleTaskState = STATE_MAPPINGS.get("ExampleTaskState").get("cls", ExampleTaskState)

class DisplayMonitorState(MonitorState):
    """Advanced Monitor State with built-in state type management."""
    
    # Class variables for state management
    state_mappings: Dict[str, str] = STATE_MAPPINGS

    # host variables
    API_URL: str = os.getenv("API_URL", "http://localhost:8000")
    WS_URL: str = f"{API_URL}/ws"
    
    @rx.var
    def task_functions(self) -> Dict[str, str]:
        """Get available task functions for current state type."""
        current_state_class: Type[MonitorState] = self.available_states.get(self.current_state_type)
        if current_state_class:
            task_functions = current_state_class.get_task_functions()
            print(f"Found {len(task_functions)} task functions")
            return task_functions
        
        return {}
    
    @rx.var
    def current_state_prefix(self) -> str:
        """Get the API prefix for the current state type."""
        current_state_class = self.available_states.get(self.current_state_type)
        if current_state_class:
            return self.state_mappings.get(current_state_class.__name__, "/api/default")
        return "/api/default"
    
    def change_state_type(self, state_type: str):
        """Change the current state type being monitored."""
        if state_type not in self.available_states:
            raise ValueError(f"Invalid state type. Available types: {list(self.available_states.keys())}")
        super().change_state_type(state_type)

    @classmethod
    def get_available_states(cls) -> Dict[str, str]:
        """Get a dictionary of available state types and their API prefixes."""
        return {
            name: cls.state_mappings.get(state_class.__name__, "/api/default")
            for name, state_class in cls.available_states.items()
        }

    @rx.event
    async def execute_current_task(self):
        """Execute the currently selected task function."""
        current_state_class: Type[MonitorState] = self.available_states.get(self.current_state_type)
        if current_state_class and self.current_task_function:
            task_instance = current_state_class()
            task_method: Callable = getattr(task_instance, self.current_task_function, None)
            if task_method is not None:
                return  task_method()
            else:
                raise ValueError(f"Task function {self.current_task_function} not found in {self.current_state_type}")
        else:
            raise ValueError("No valid state type or task function selected")

# Export the classes and mappings
__all__ = [
    "MonitorState",
    "DisplayMonitorState",
    "STATE_MAPPINGS",
]