from pydantic import BaseModel
from app.config import APP_DISPLAY_NAME

class SubscriptionArgs(BaseModel):
    """Input arguments for ConvertKit email subscription."""
    email: str
    signup_source: str = APP_DISPLAY_NAME
