from pydantic import BaseModel

class InputArgs(BaseModel):
    """Input arguments for the task."""
    name: str
    age: int