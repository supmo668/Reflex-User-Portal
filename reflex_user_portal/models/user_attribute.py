from typing import List, Optional, Dict, Any
from sqlmodel import Field, Column, JSON

import sqlmodel
import reflex as rx

class UserAttribute(rx.Model, table=True):
    user: Optional["User"] = sqlmodel.Relationship(
        back_populates="user_attribute"
    )
    user_collections: Dict[str, Any] = Field(
        default={},
        sa_column=Column(JSON)
    )