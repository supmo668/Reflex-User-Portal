"""Models package."""
from .admin.user import User, UserType, UserAttribute, CollectionResponse
from .admin.admin_config import AdminConfig


__all__ = ["User", "UserType", "UserAttribute", "CollectionResponse", "AdminConfig"]


# Factory mapping for models
MODEL_FACTORY = {
    "AdminConfig": AdminConfig,
}