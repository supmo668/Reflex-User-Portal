"""User model for the application."""
from typing import Optional, Dict, Any
from enum import Enum
from datetime import datetime, timezone

import reflex as rx
from sqlmodel import Field, Column, JSON, Relationship
from pydantic import BaseModel, SkipValidation

# Add imports for Subscription and SubscriptionFeature
from typing import List
from ...models.admin.subscription import Subscription

class UserType(str, Enum):
    """User type enumeration."""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

class UserAttribute(rx.Model, table=True):
    """
    User attribute model for storing user-specific data including collections.
    Collections are stored as a dictionary where:
    - key: collection name
    - value: dictionary containing collection data including entries
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    user: Optional["User"] = Relationship(
        back_populates="user_attribute",
    )
    collections: Dict[str, Any] = Field(
        default={},
        sa_column=Column(JSON)
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

    # Relationship to user attributes (including collections)
    user_attribute: Optional[UserAttribute] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"uselist": False}
    )
    # Add subscriptions relationship
    subscriptions: List[Subscription] = Relationship(back_populates="user")
    
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


class UserAttributeModel(BaseModel):
    """Response model for UserAttribute data"""
    id: Optional[int] = None
    user_id: int
    collections: Dict[str, Dict[str, Any]] = {}
    user: Dict[str, Any]

class CollectionResponse(BaseModel):
    """Response model for collection data"""
    collections: Dict[str, Dict[str, Any]]


class UserModel(BaseModel):
    """Response model for User data"""
    id: Optional[int] = None
    email: str
    clerk_id: str = ""
    user_type: UserType = UserType.GUEST
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    user_attribute: Dict[str, Any] = None