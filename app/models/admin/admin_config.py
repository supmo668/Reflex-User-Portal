"""Admin config model for the application."""
from typing import Optional, Dict, Any
import yaml
import reflex as rx
import sqlalchemy
from sqlalchemy import DateTime, JSON
from sqlmodel import Field, Column
from enum import Enum
from datetime import datetime



class AdminConfig(rx.Model, table=True):
    """Admin config model that stores workflow configuration as YAML."""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    version: float = Field(default=0.1)
    
    # Store as JSON in database but represent as YAML in application
    configuration: Dict[str, Any] = Field(
        default={},
        sa_column=Column(JSON)
    )
    created_at: datetime = Field(
        default=None,
        sa_column=Column(
            "created_at",
            DateTime(timezone=True),
            server_default=sqlalchemy.func.now()
        )
    )
    updated_at: datetime = Field(
        default=None,
        sa_column=Column(
            "updated_at",
            DateTime(timezone=True),
            server_default=sqlalchemy.func.now(),
            onupdate=sqlalchemy.func.now()
        )
    )