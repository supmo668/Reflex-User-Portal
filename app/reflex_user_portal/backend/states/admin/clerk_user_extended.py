"""Extended Clerk User state with metadata management capabilities."""

import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, ClassVar
from enum import Enum

import reflex as rx
import clerk_backend_api
from reflex_clerk_api import ClerkUser, ClerkState
from reflex_clerk_api.clerk_provider import get_user, MissingUserError

from app.models.admin.user import UserType
from app.config import ADMIN_USER_EMAILS

logger = logging.getLogger(__name__)


class ExtendedClerkUser(ClerkUser):
    """Extended ClerkUser with additional fields and metadata management capabilities.
    
    This class extends the base ClerkUser to include additional user fields
    and provides methods to interact with Clerk's public and private metadata.
    """
    
    # Additional user fields from the User model
    clerk_id: str = ""
    client_id: str = ""
    user_type: str = UserType.GUEST.value
    avatar_url: str = "/chat/avatar_default.webp"
    is_active: bool = True
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    # Metadata fields
    public_metadata: Dict[str, Any] = {}
    private_metadata: Dict[str, Any] = {}
    
    # Subscription and settings from metadata
    subscription_status: str = "free"
    subscription_plan: str = "basic"
    settings: Dict[str, Any] = {}
    user_collections: Dict[str, Any] = {}
    
    # Class variable to track registration
    _is_registered: ClassVar[bool] = False

    @rx.event
    async def load_user(self) -> None:
        """Load user information from Clerk including metadata."""
        try:
            user: clerk_backend_api.models.User = await get_user(self)
        except MissingUserError:
            logger.debug("Clearing user state")
            self.reset()
            return

        logger.debug("Updating extended user state")
        
        # Load basic user info (from parent class)
        self.first_name = (
            user.first_name
            if user.first_name and user.first_name != clerk_backend_api.UNSET
            else ""
        )
        self.last_name = (
            user.last_name
            if user.last_name and user.last_name != clerk_backend_api.UNSET
            else ""
        )
        self.username = (
            user.username
            if user.username and user.username != clerk_backend_api.UNSET
            else ""
        )
        self.email_address = (
            user.email_addresses[0].email_address if user.email_addresses else ""
        )
        self.has_image = True if user.has_image is True else False
        self.image_url = user.image_url or ""
        
        # Load extended fields
        self.clerk_id = user.id or ""
        self.avatar_url = user.image_url or "/chat/avatar_default.webp"
        
        # Convert Clerk timestamp (Unix timestamp in milliseconds) to datetime
        if user.created_at and user.created_at != clerk_backend_api.UNSET:
            if isinstance(user.created_at, int):
                # Clerk returns Unix timestamp in milliseconds
                self.created_at = datetime.fromtimestamp(user.created_at / 1000, tz=timezone.utc)
            elif isinstance(user.created_at, datetime):
                self.created_at = user.created_at
            else:
                self.created_at = None
        else:
            self.created_at = None
        
        self.last_login = datetime.now(timezone.utc)
        
        # Load metadata
        self.public_metadata = user.public_metadata or {}
        self.private_metadata = user.private_metadata or {}
        
        # Extract specific fields from metadata
        self._load_metadata_fields()
        
        # Determine user type
        self._determine_user_type()

    def _load_metadata_fields(self) -> None:
        """Load specific fields from metadata."""
        # Load from public metadata
        self.subscription_status = self.public_metadata.get("subscription_status", "free")
        self.subscription_plan = self.public_metadata.get("subscription_plan", "basic")
        self.settings = self.public_metadata.get("settings", {})
        
        # Load from private metadata
        self.user_collections = self.private_metadata.get("user_collections", {})
        self.client_id = self.private_metadata.get("client_id", "")
        self.is_active = self.private_metadata.get("is_active", True)

    def _determine_user_type(self) -> None:
        """Determine user type based on email and metadata."""
        admin_emails = ADMIN_USER_EMAILS
        if self.email_address in admin_emails:
            self.user_type = UserType.ADMIN.value
        elif self.email_address:
            self.user_type = UserType.USER.value
        else:
            self.user_type = UserType.GUEST.value

    @rx.event
    async def update_public_metadata(self, metadata: Dict[str, Any]) -> None:
        """Update user's public metadata in Clerk.
        
        Args:
            metadata: Dictionary of metadata to update
        """
        try:
            clerk_state = await self.get_state(ClerkState)
            if not clerk_state.user_id:
                logger.warning("No user_id available for metadata update")
                return
                
            # Update metadata in Clerk
            updated_user = await clerk_state.client.users.update_async(
                user_id=clerk_state.user_id,
                public_metadata=metadata
            )
            
            # Update local state
            self.public_metadata.update(metadata)
            self._load_metadata_fields()
            
            logger.debug(f"Updated public metadata: {metadata}")
            
        except Exception as e:
            logger.error(f"Error updating public metadata: {e}")
            raise

    @rx.event
    async def update_private_metadata(self, metadata: Dict[str, Any]) -> None:
        """Update user's private metadata in Clerk.
        
        Args:
            metadata: Dictionary of metadata to update
        """
        try:
            clerk_state = await self.get_state(ClerkState)
            if not clerk_state.user_id:
                logger.warning("No user_id available for metadata update")
                return
                
            # Update metadata in Clerk
            updated_user = await clerk_state.client.users.update_async(
                user_id=clerk_state.user_id,
                private_metadata=metadata
            )
            
            # Update local state
            self.private_metadata.update(metadata)
            self._load_metadata_fields()
            
            logger.debug(f"Updated private metadata: {metadata}")
            
        except Exception as e:
            logger.error(f"Error updating private metadata: {e}")
            raise

    @rx.event
    async def get_public_metadata(self) -> Dict[str, Any]:
        """Retrieve user's public metadata from Clerk.
        
        Returns:
            Dictionary of public metadata
        """
        try:
            clerk_state = await self.get_state(ClerkState)
            if not clerk_state.user_id:
                logger.warning("No user_id available for metadata retrieval")
                return {}
                
            user = await clerk_state.client.users.get_async(user_id=clerk_state.user_id)
            self.public_metadata = user.public_metadata or {}
            return self.public_metadata
            
        except Exception as e:
            logger.error(f"Error retrieving public metadata: {e}")
            return {}

    @rx.event
    async def get_private_metadata(self) -> Dict[str, Any]:
        """Retrieve user's private metadata from Clerk.
        
        Returns:
            Dictionary of private metadata
        """
        try:
            clerk_state = await self.get_state(ClerkState)
            if not clerk_state.user_id:
                logger.warning("No user_id available for metadata retrieval")
                return {}
                
            user = await clerk_state.client.users.get_async(user_id=clerk_state.user_id)
            self.private_metadata = user.private_metadata or {}
            return self.private_metadata
            
        except Exception as e:
            logger.error(f"Error retrieving private metadata: {e}")
            return {}

    @rx.event
    async def update_subscription_status(self, status: str, plan: str = None) -> None:
        """Update user's subscription status.
        
        Args:
            status: Subscription status (e.g., 'free', 'premium', 'enterprise')
            plan: Optional subscription plan name
        """
        metadata = {"subscription_status": status}
        if plan:
            metadata["subscription_plan"] = plan
            
        await self.update_public_metadata(metadata)

    @rx.event
    async def update_user_settings(self, settings: Dict[str, Any]) -> None:
        """Update user's settings in public metadata.
        
        Args:
            settings: Dictionary of user settings
        """
        await self.update_public_metadata({"settings": settings})

    @rx.event
    async def add_to_collection(self, collection_name: str, item: Any) -> None:
        """Add item to a user collection stored in private metadata.
        
        Args:
            collection_name: Name of the collection
            item: Item to add to the collection
        """
        collections = self.user_collections.copy()
        if collection_name not in collections:
            collections[collection_name] = []
        
        if item not in collections[collection_name]:
            collections[collection_name].append(item)
            await self.update_private_metadata({"user_collections": collections})

    @rx.event
    async def remove_from_collection(self, collection_name: str, item: Any) -> None:
        """Remove item from a user collection.
        
        Args:
            collection_name: Name of the collection
            item: Item to remove from the collection
        """
        collections = self.user_collections.copy()
        if collection_name in collections and item in collections[collection_name]:
            collections[collection_name].remove(item)
            await self.update_private_metadata({"user_collections": collections})

    @rx.event
    async def clear_collection(self, collection_name: str) -> None:
        """Clear all items from a user collection.
        
        Args:
            collection_name: Name of the collection to clear
        """
        collections = self.user_collections.copy()
        collections[collection_name] = []
        await self.update_private_metadata({"user_collections": collections})

    @rx.var
    def is_admin(self) -> bool:
        """Check if current user is admin."""
        return self.user_type == UserType.ADMIN.value

    @rx.var
    def is_premium_user(self) -> bool:
        """Check if user has premium subscription."""
        return self.subscription_status in ["premium", "enterprise"]

    @rx.var
    def full_name(self) -> str:
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.username or self.email_address or "Guest"
