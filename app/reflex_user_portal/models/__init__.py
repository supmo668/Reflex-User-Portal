"""Models package."""
from .admin.user import User, UserType, UserAttribute, CollectionResponse
from .admin.admin_config import AdminConfig
from .admin.subscription import SubscriptionFeature


__all__ = ["User", "UserType", "UserAttribute", "CollectionResponse", "AdminConfig", "SubscriptionFeature"]


# Factory mapping for models
MODEL_FACTORY = {
    "AdminConfig": AdminConfig,
    "SubscriptionFeature": SubscriptionFeature,
}