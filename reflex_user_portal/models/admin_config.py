"""Admin config model for the application."""
from typing import Optional, Dict, Any
import yaml
import reflex as rx
from sqlmodel import Field, Column, JSON
from enum import Enum
from datetime import datetime, timezone
from pydantic import validator, field_serializer, field_validator


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
    
    created_at: Optional[datetime] = Field(default=datetime.now(timezone.utc))
    last_updated: Optional[datetime] = Field(default=datetime.now(timezone.utc))
  
    # Provide a method to get configuration as YAML
    def get_yaml_config(self) -> str:
        """Return the configuration as a YAML string."""
        return yaml.dump(self.configuration, sort_keys=False)
    
    # Method to set configuration from YAML
    def set_yaml_config(self, yaml_str: str) -> None:
        """Set configuration from a YAML string."""
        self.configuration = yaml.safe_load(yaml_str)

# Factory mapping for models
MODEL_FACTORY = {
    "admin_config": AdminConfig,
}