import os
import importlib
import inspect
from typing import Dict, Type, List

import reflex as rx
from reflex_user_portal.backend.wrapper.models import TaskData
from reflex_user_portal.backend.wrapper.task import monitored_background_task, TaskContext
from .base import MonitorState
from .example_task import ExampleTaskState


def discover_task_states() ->Dict[str, dict]:
    """
    Dynamically discover all task state classes in the task module directory.
    Returns:
        Tuple of (state_mappings)
    """
    states_dir = os.path.dirname(__file__)
    state_mappings: Dict[str, str] = {}
    
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
                    # Optionally: api_prefix = f"/api/{module_name}/{name.lower()}"  for multiple state class in a module 
                    state_mappings[obj.__name__] = {
                        "api_prefix": f"/api/{module_name}",
                        "ws_prefix": f"/ws/{module_name}",
                        "cls": obj
                    }

                    
        except ImportError as e:
            print(f"Warning: Could not import module {module_name}: {e}")
            continue
            
    return state_mappings

# Discover all task states
STATE_MAPPINGS = discover_task_states()
ExampleTaskState = STATE_MAPPINGS.get("ExampleTaskState", {}).get("cls", ExampleTaskState)
print(f"Discovered task states: {list(STATE_MAPPINGS.keys())}")

class DisplayMonitorState(MonitorState):
    """Advanced Monitor State with built-in state type management."""
    current_state_type: str = "ExampleTaskState"
    # Class variables for state management
    state_mappings: Dict[str, dict] = STATE_MAPPINGS
    @rx.var
    def current_state_class(self) -> Type[MonitorState]:
        """Get the current state class based on the current state type."""
        return self.state_mappings.get(self.current_state_type).get("cls", ExampleTaskState)
    
    # @rx.var
    # async def active_tasks(self) -> List[TaskData]:
    #     """Get active tasks from the current state."""
    #     # Get an instance of the current state class
    #     task_state = await self.get_state(self.current_state_class)
    #     return task_state.active_tasks
    
    # @rx.var
    # async def completed_tasks(self) -> List[TaskData]:
    #     """Get active tasks from the current state."""
    #     # Get an instance of the current state class
    #     task_state = await self.get_state(self.current_state_class)
    #     return task_state.completed_tasks
    
    @rx.var
    def task_functions(self) -> Dict[str, str]:
        """Get available task functions for current state type."""
        if self.current_state_class and hasattr(self.current_state_class, "get_task_functions"):
            task_functions = self.current_state_class.get_task_functions()
            print(f"Found {len(task_functions)} task functions")
            return task_functions
        return {}
    
    @rx.var
    def current_state_prefix(self) -> str:
        """Get the API prefix for the current state type."""
        if self.current_state_class is not None:
            return self.state_mappings.get(self.current_state_type).get("api_prefix", "/api/default")
        return "/api/default"
    
    @rx.event
    def change_state_type(self, state_type: str):
        """Change the current state type being monitored."""
        self.current_state_type = state_type

    @rx.event
    def execute_current_task(self):
        """Execute the currently selected task function."""
        if self.current_state_class and self.current_task_function:
            # Get the launcher method from the class
            launcher_name = f"launch_{self.current_task_function}"
            launcher = getattr(self.current_state_class, launcher_name, None)
            if launcher:
                # Return the launcher event which will properly handle the background task
                return launcher(self)
            else:
                raise ValueError(f"Launch handler {launcher_name} not found in {self.current_state_type}")
        else:
            raise ValueError("No valid state type or task function selected")

# Export the classes and mappings
__all__ = [
    "MonitorState",
    "DisplayMonitorState",
    "STATE_MAPPINGS",
]