from .task import setup_api as setup_task_api

__all__ = ["setup_task_api"]

def setup_api(app):
    setup_task_api(app)