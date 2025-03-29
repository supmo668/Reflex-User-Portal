"""User model for the application."""
from typing import List, Optional, Dict, Any
from enum import Enum
from sqlmodel import Field, Column, JSON

import sqlmodel
import reflex as rx
from pydantic import BaseModel

from datetime import datetime, timezone

class UserType(str, Enum):
    """User type enumeration."""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

class UserAttribute(rx.Model, table=True):
    """
    [Optional] User attribute model for storing user-specific data.
    """
    user_id: int = sqlmodel.Field(foreign_key="user.id")
    user: Optional["User"] = sqlmodel.Relationship(
        back_populates="user_attribute"
    )
    user_collections: Dict[str, Any] = Field(
        default={},
        sa_column=Column(JSON)
    )

class UserAPI(BaseModel):
    """API-compatible user model."""
    id: Optional[int] = None
    email: str
    clerk_id: str
    user_type: UserType
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    @classmethod
    def from_user(cls, user: "User") -> "UserAPI":
        """Convert User model to UserAPI model."""
        return cls(
            id=user.id,
            email=user.email,
            clerk_id=user.clerk_id,
            user_type=user.user_type,
            first_name=user.first_name,
            last_name=user.last_name,
            avatar_url=user.avatar_url,
            is_active=user.is_active,
            created_at=user.created_at,
            last_login=user.last_login
        )

class User(rx.Model, table=True):
    """Base user model."""
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    clerk_id: str = Field(unique=True, default="")
    user_type: UserType = UserType.GUEST
    
    # User information
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    
    # Account status
    is_active: bool = Field(default=True)
    created_at: Optional[datetime] = Field(default=datetime.now(timezone.utc))
    last_login: Optional[datetime] = None

    # custom user attributes
    user_attribute: UserAttribute = sqlmodel.Relationship(
        back_populates="user"
    )
    
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