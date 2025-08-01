"""
Key module for dynamically discovering and manages task states for a monitoring system.
It provides a base class for states and a display class that handles
state management, task execution, and command formatting.
task functions decorated with `@monitored_background_task` are automatically monitored.
"""
import os
import json
import importlib
import inspect
from pydantic import BaseModel
from typing import Dict, Type, Optional

import reflex as rx

from .base import MonitorState
from ....utils.logger import get_logger
logger = get_logger(__name__)


def discover_task_states() -> Dict[str, dict]:
    """
    Dynamically discover all task state classe 
    Returns:
        Dict[str, dict]: A dictionary of state mappings
        Details:
            Key: State name
            Value: State info
            State info:
                api_prefix: API prefix for the state
                ws_prefix: WebSocket prefix for the state
                cls: State class
    """
    states_dir = os.path.dirname(__file__)
    state_mappings: Dict[str, dict] = {}
    
    # Process all items in the directory
    for item in os.listdir(states_dir):
        # Skip special files and directories
        if item in {'__init__.py', '__pycache__', 'base.py'}:
            continue
            
        item_path = os.path.join(states_dir, item)
        
        if os.path.isfile(item_path) and item.endswith('.py'):
            # Handle direct Python files
            module_name = item[:-3]
            _process_module(module_name, state_mappings)
            
        elif os.path.isdir(item_path):
            # Handle package directories with __init__.py
            init_path = os.path.join(item_path, '__init__.py')
            if os.path.exists(init_path):
                try:
                    # Import the package
                    package = importlib.import_module(f".{item}", package=__package__)
                    
                    # First try processing exposed modules in __all__
                    if hasattr(package, '__all__'):
                        for exposed_name in package.__all__:
                            # Get the actual object that was exposed
                            exposed_obj = getattr(package, exposed_name)
                            if (inspect.isclass(exposed_obj) and 
                                issubclass(exposed_obj, MonitorState) and 
                                exposed_obj != MonitorState):
                                state_mappings[exposed_name] = {
                                    "api_prefix": f"/api/{item}",
                                    "ws_prefix": f"/ws/{item}",
                                    "cls": exposed_obj,
                                }
                                # Make the class available at package level
                                globals()[exposed_name] = exposed_obj
                                
                except ImportError as e:
                    logger.info(f"Warning: Could not import package {item}: {e}")
                    
    return state_mappings

def _process_module(module_name: str, state_mappings: Dict[str, dict]):
    """Process a module and add any found state classes to the mappings."""
    try:
        # Import using absolute path
        module = importlib.import_module(f".{module_name}", package=__package__)
        
        # Find MonitorState subclasses
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and 
                issubclass(obj, MonitorState) and 
                obj != MonitorState):
                state_mappings[name] = {
                    "api_prefix": f"/api/{module_name.split('.')[-1]}",
                    "ws_prefix": f"/ws/{module_name.split('.')[-1]}",
                    "cls": obj,
                }
                # Make the class available at package level
                globals()[name] = obj
    except ImportError as e:
        logger.info(f"Warning: Could not import {module_name}: {e}")

# Discover states once at module load
# STATE_MAPPINGS is a dictionary of mappings from state name to state info
# Details:
#     Key: State name
#     Value: State info
#     State info:
#         api_prefix: API prefix for the state
#         ws_prefix: WebSocket prefix for the state
#         cls: State class
STATE_MAPPINGS: Dict[str, dict] = discover_task_states()
logger.info(f"Discovered task states: {list(STATE_MAPPINGS.keys())}")

from ....backend.api.commands import format_command

class DisplayMonitorState(MonitorState):
    """Advanced Monitor State with built-in state type management."""
    current_state_type: str = list(STATE_MAPPINGS.keys())[0]
    # Class variables for state management
    state_mappings: Dict[str, dict] = STATE_MAPPINGS

    @rx.var
    def current_state_info(self) -> dict:
        """Get the current state information."""
        return STATE_MAPPINGS.get(self.current_state_type, {})
    @rx.var
    def current_state_class(self) -> Optional[Type[MonitorState]]:
        """Get the current state class based on the current state type."""
        return self.current_state_info.get("cls")
    
    @rx.var
    def avail_task_functions(self) -> Dict[str, str]:
        return self.current_state_class.get_task_functions()
    
    @rx.var
    def task_functions(self) -> Dict[str, str]:
        """
        Get available task functions for current state type.
        """
        if self.current_state_class and hasattr(self.current_state_class, "get_task_functions"):
            logger.info(f"Found {len(self.avail_task_functions)} task functions named {list(self.avail_task_functions.keys())}")
            self.current_task_function = list(self.avail_task_functions.keys())[0]
            return self.avail_task_functions
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
        return DisplayMonitorState.preselect_task_function
    
    # @rx.event
    def current_task_method(self) -> Optional[callable]:
        """Get the current task function name."""
        return getattr(
            self.current_state_class, self.current_task_function, None)
    
    @rx.event
    def preselect_task_function(self):
        """Preselect the first task function. (for onload event)"""
        if len(self.task_functions) == 0:
            return
        self.current_task_function = list(self.task_functions.keys())[0]
        logger.debug(f"Preselected task function: {self.current_task_function}")
        
    # TODO: Untested function - require validation
    @rx.event
    async def execute_current_task(self):
        """Execute the currently selected task function."""
        if self.current_state_class and self.current_task_function:
            # Get the launcher method from the class
            if self.current_task_method:
                # Set the task arguments in the target state before launching
                # async with self.current_state_class as target_state:
                #     # Set any required input variables on target_state here
                #     if self.tasks_argument:
                #         target_state.task_args = self.tasks_argument
                
                # Return the launcher event which will properly handle the background task
                return self.current_task_method
            else:
                raise ValueError(f"Launch handler {self.current_task_function} not found in {self.current_state_type}")
        else:
            raise ValueError("No valid state type or task function selected")

    @rx.event
    def change_task_function(self, function_name: str):
        """Change the current task function."""
        if function_name in self.task_functions:
            self.current_task_function = function_name
        else:
            raise ValueError(f"Invalid task function. Available functions in {self.current_state_type}: {list(self.task_functions.keys())}")

    
    ## The following functions are used to format the commands for the API
    ## and WebSocket endpoints.
    
    @rx.var
    def formatted_curl_body(self) -> str:
        """Format task arguments into a curl -d string using default args."""
        if not self.current_task_function or not self.current_state_class:
            return ""
            
        try:
            # Get the method directly from the class
            method_name = self.current_task_function
            logger.debug(f"Looking for method: {method_name} in class {self.current_state_class.__name__}")
            current_method = getattr(self.current_state_class, method_name, None)
            
            if not current_method:
                logger.debug(f"Method {method_name} not found in {self.current_state_class.__name__}")
                return ""
            
            logger.debug(f"Found method: {current_method}")
            
            # Handle different types of methods
            original_func = None
            
            # Case 1: Regular Reflex event handler with fn attribute
            if hasattr(current_method, 'fn'):
                logger.debug(f"Method has fn attribute: {current_method.fn}")
                original_func = current_method.fn
            # Case 2: Direct function with monitored_background_task decorator
            elif hasattr(current_method, 'is_monitored_background_task'):
                logger.debug(f"Method has is_monitored_background_task attribute")
                # Check if this is a wrapper with original_func attribute
                if hasattr(current_method, 'original_func'):
                    logger.debug(f"Found original_func attribute: {current_method.original_func}")
                    original_func = current_method.original_func
                else:
                    original_func = current_method
            else:
                logger.debug(f"Method is not a monitored background task")
                return ""
                
            # Inspect signature to find task_args parameter
            sig = inspect.signature(original_func)
            logger.debug(f"Method signature: {sig}")
            logger.debug(f"Parameter types: {[p for p in sig.parameters.values()]}")
            
            # Look for task_args parameter and get its default value
            for param_name, param in sig.parameters.items():
                logger.debug(f"Checking parameter: {param_name}, annotation: {param.annotation}, default: {'has default' if param.default is not param.empty else 'no default'}")
                if param_name == "task_args":
                    logger.debug(f"Found task_args parameter with annotation: {param.annotation}")
                    # Get the default value if it exists
                    if param.default is not param.empty:
                        default_value = param.default
                        # Convert default value to dict if it's a pydantic model
                        logger.debug(f"Default value type: {type(default_value)}, dir: {dir(default_value)}")
                        if isinstance(default_value, BaseModel):
                            default_dict = default_value.model_dump()
                            logger.debug(f"Converted to dict: {default_dict}")
                            return f"-d '{json.dumps(default_dict, indent=2, sort_keys=True)}'"
                        elif hasattr(default_value, 'model_dump'):
                            # Handle case where it's a Pydantic model but not recognized as BaseModel subclass
                            logger.debug(f"Object has model_dump method but is not recognized as BaseModel")
                            default_dict = default_value.model_dump()
                            logger.debug(f"Converted to dict: {default_dict}")
                            return f"-d '{json.dumps(default_dict, indent=2, sort_keys=True)}'"
                        else:
                            logger.debug(f"Default value is not a BaseModel: {type(default_value)}")
                    else:
                        logger.debug("task_args parameter has no default value")
                    break
            logger.debug("No task_args parameter found or no valid default value")
            return ""
            
        except Exception as e:
            logger.error(f"Error formatting curl body: {e}")
            return ""
           
    def get_command(self, cmd_type: str, state_name: str, **kwargs) -> str:
        """Helper to format commands with current state info"""
        state_info = STATE_MAPPINGS[state_name]
        return format_command(
            cmd_type,
            state_info,
            client_token=self.client_token,
            **kwargs
        )
    @rx.var
    def base_api_path(self) -> str:
        """Get the base API path for the current state type."""
        return self.get_command("base", self.current_state_type)
    @rx.var
    def status_command(self) -> str:
        """Get the command to check the status of all tasks."""
        return self.get_command("status", self.current_state_type)
    @rx.var
    def task_status_command(self) -> str:
        """Get the command to check the status of a specific task."""
        return self.get_command("status_by_id", self.current_state_type, task_id="{task_id}")
    @rx.var
    def start_command(self) -> str:
        """Get the command to start a task."""
        return self.get_command("start", self.current_state_type, session_id="{session_id}", task_name=self.current_task_function)
    @rx.var
    def result_command(self) -> str:
        """Get the command to check the result of a task."""
        return self.get_command("result", self.current_state_type, task_id="{task_id}")
    @rx.var
    def ws_status_command(self) -> str:
        """Get the command to check the status of all tasks via WebSocket."""
        return self.get_command("ws_all", self.current_state_type)
    @rx.var
    def ws_task_command(self) -> str:
        """Get the command to check the status of a specific task via WebSocket."""
        return self.get_command("ws_task", self.current_state_type, task_id="{task_id}")
        
# Export discovered classes
__all__ = ["MonitorState", "DisplayMonitorState", "STATE_MAPPINGS"] + list(STATE_MAPPINGS.keys())
