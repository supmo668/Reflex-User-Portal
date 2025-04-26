from .task import setup_api as setup_task_api
from .clerk_user import setup_api as setup_clerk_user_api
from ..states.task import STATE_MAPPINGS

# setting up multiple task APIs with different states
def setup_state_task_apis(app):
    """
    Set up multiple task APIs on all the discovered states.
    """   
    for name, state_info in STATE_MAPPINGS.items():
        # Extract the state class and API prefix
        print(f"Setting up API for state: {name} at {state_info['api_prefix']}")
        setup_task_api(app, state_info)

def setup_api(app):
    setup_state_task_apis(app)
    setup_clerk_user_api(app)
    
__all__ = ["setup_state_task_apis"]
