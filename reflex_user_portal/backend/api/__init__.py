from .task import setup_api as setup_task_api
from ..states.task import STATE_MAPPINGS

# setting up multiple task APIs with different states
def setup_state_task_apis(app):
    """
    Example of how to set up multiple task APIs for different states.
    """   
    for name, state_info in STATE_MAPPINGS.items():
        # Extract the state class and API prefix
        print(f"Setting up API for state: {name} at {state_info['api_prefix']}")
        setup_task_api(app, state_info)

__all__ = ["setup_state_task_apis"]
