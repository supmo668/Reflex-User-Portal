import reflex as rx

from .task import TaskAPI
from .client import ClientAPI
from .clerk_user import setup_api as setup_clerk_user_api
from ..states.task import STATE_MAPPINGS

# setting up multiple task APIs with different states
def setup_state_task_apis(app):
    """
    Set up multiple task APIs on all the discovered states.
    
    This function creates TaskAPI instances for each state in STATE_MAPPINGS,
    organizing them by state name for better API documentation.
    """   
    for state_name, state_info in STATE_MAPPINGS.items():
        # Extract the state class and API prefix
        print(f"Setting up API for state: {state_name} at {state_info['api_prefix']}")
        # Pass state_name to TaskAPI constructor for better route organization
        TaskAPI(app, state_name, state_info)

def setup_api(app: rx.App):
    setup_state_task_apis(app)
    setup_clerk_user_api(app.api_transformer)
    
__all__ = ["setup_state_task_apis"]
