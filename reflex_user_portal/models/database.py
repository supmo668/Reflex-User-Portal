"""Database configuration and utilities."""
import os
from sqlmodel import SQLModel, create_engine

# Get database URL from environment or use default SQLite database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./spyglass.db")

# Create engine with echo for development
engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    """Create all tables in the database."""
    SQLModel.metadata.create_all(engine)
