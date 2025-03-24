import os
import importlib
import inspect
from typing import Dict, Type, ClassVar, Optional

import reflex as rx
from .base import MonitorState

def discover_task_states() -> Dict[str, dict]:
    """Dynamically discover all task state classes."""
    states_dir = os.path.dirname(__file__)
    state_mappings: Dict[str, dict] = {}
    
    # First, collect all the mappings
    for item in os.listdir(states_dir):
        if item in {'__init__.py', '__pycache__', 'base.py'} or not item.endswith('.py'):
            continue
            
        module_name = item[:-3]
        try:
            # Import using absolute path
            module = importlib.import_module(f".{module_name}", package=__package__)
            
            # Find MonitorState subclasses
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, MonitorState) and 
                    obj != MonitorState):
                    state_mappings[name] = {
                        "api_prefix": f"/api/{module_name}",
                        "ws_prefix": f"/ws/{module_name}",
                        "cls": obj,
                    }
                    # Make the class available at package level
                    globals()[name] = obj
        except ImportError as e:
            print(f"Warning: Could not import {module_name}: {e}")
            
    return state_mappings

# Discover states once at module load
STATE_MAPPINGS: ClassVar[Dict[str, dict]] = discover_task_states()
print(f"Discovered task states: {list(STATE_MAPPINGS.keys())}")

class DisplayMonitorState(MonitorState):
    """Advanced Monitor State with built-in state type management."""
    current_state_type: str = "ExampleTaskState"
    # Class variables for state management
    state_mappings: Dict[str, dict] = STATE_MAPPINGS

    @rx.var
    def current_state_info(self) -> dict:
        """Get the current state information."""
        return self.state_mappings.get(self.current_state_type, {})
    @rx.var
    def current_state_class(self) -> Optional[Type[MonitorState]]:
        """Get the current state class based on the current state type."""
        return self.current_state_info.get("cls")
    
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
            print(f"Found {len(task_functions)} task functions named {list(task_functions.keys())}")
            return task_functions
        return {}
    
    @rx.var
    def current_state_prefix(self) -> str:
        """Get the API prefix for the current state type."""
        if self.current_state_class is not None:
            return self.current_state_info.get("api_prefix", "/api/default")
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
            launcher = getattr(self.current_state_class, self.current_task_function, None)
            if launcher:
                # Return the launcher event which will properly handle the background task
                yield launcher
            else:
                raise ValueError(f"Launch handler {self.current_task_function} not found in {self.current_state_type}")
        else:
            raise ValueError("No valid state type or task function selected")

# Export discovered classes
__all__ = ["MonitorState", "DisplayMonitorState", "STATE_MAPPINGS"] + list(STATE_MAPPINGS.keys())