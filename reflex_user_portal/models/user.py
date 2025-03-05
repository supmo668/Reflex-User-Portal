"""User model for the application."""
from typing import Optional
import reflex as rx
from sqlmodel import Field, SQLModel
from enum import Enum
from datetime import datetime, timezone


class UserType(str, Enum):
    """User type enumeration."""
    ADMIN = "admin"
    USER = "user"


class User(rx.Model, table=True):
    """Base user model."""
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    clerk_id: str = Field(unique=True)
    user_type: Optional[UserType] = None
    
    # User information
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    
    # Account status
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    last_login: Optional[datetime] = None
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        return "Anonymous"
