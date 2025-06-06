from typing import Optional
import datetime
from datetime import timezone

import reflex as rx
import sqlalchemy

import sqlmodel

class SubscriptionFeature(rx.Model, table=True):
    id: int = sqlmodel.Field(default=None, primary_key=True)
    name: str

    # impose other subscription limits and constraints
class Subscription(rx.Model, table=True):
    user_id: int = sqlmodel.Field(foreign_key="user.id")
    user: Optional["User"] = sqlmodel.Relationship(back_populates="subscriptions")
    feature_id: int = sqlmodel.Field(foreign_key="subscriptionfeature.id")
    feature: Optional["SubscriptionFeature"] = sqlmodel.Relationship(back_populates=None)
    start_date: datetime.date
    end_date: datetime.date
    created_at: datetime.datetime = sqlmodel.Field(
        default_factory=lambda: datetime.datetime.now(timezone.utc),
        sa_column=sqlalchemy.Column(
            "created_at",
            sqlalchemy.DateTime(timezone=True),
            server_default=sqlalchemy.func.now(),
        ),
    )
    updated_at: datetime.datetime = sqlmodel.Field(
        default_factory=lambda: datetime.datetime.now(timezone.utc),
        sa_column=sqlalchemy.Column(
            "updated_at",
            sqlalchemy.DateTime(timezone=True),
            server_default=sqlalchemy.func.now(),
            onupdate=sqlalchemy.func.now(),
        ),
    )
    auto_renew: bool = False
    is_active: bool = True
    cancellation_notes: Optional[str] = None