from .task import setup_api as setup_task_api
from ..states.task import STATE_MAPPINGS
__all__ = ["setup_task_api"]

# def setup_api(app):
#     setup_task_api(app)

# Example of setting up multiple task APIs with different states
def setup_task_apis(app):
    """
    Example of how to set up multiple task APIs for different states.
    """   
    setup_task_api(app, STATE_MAPPINGS)