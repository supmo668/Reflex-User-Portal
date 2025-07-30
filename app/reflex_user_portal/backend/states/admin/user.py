"""User state management using Clerk-based authentication and metadata storage."""
from datetime import datetime, timezone
from typing import Optional, Dict, Any

import reflex as rx
import reflex_clerk_api as clerk

from app.models.admin.user import UserType
from ....utils.logger import get_logger
from .clerk_user_extended import ExtendedClerkUser

logger = get_logger(__name__)


class UserAuthState(ExtendedClerkUser):
    """User authentication state management using ExtendedClerkUser.
    
    This class manages user authentication and data storage entirely through Clerk,
    eliminating the need for local database synchronization.
    """
    
    # Redirect management
    redirect_after_login: Optional[str] = None
    
    @rx.event
    async def sync_auth_state(self):
        """Handle user authentication state changes using Clerk metadata.
        
        - User signing in:
            - Load user data from Clerk including metadata
            - Update last login timestamp
            - Handle redirect to pre-login page
        - User signing out or browsing as guest:
            - Reset user state to guest
            - Save current page for post-login redirect
        """
        # Get clerk authentication state
        clerk_state = await self.get_state(clerk.ClerkState)
        logger.debug("Clerk authentication state: %s", clerk_state.is_signed_in)
        
        try:
            if clerk_state.is_signed_in:
                # User is authenticated - load their data from Clerk
                await self.load_user()
                
                # Update last login timestamp in private metadata
                await self.update_private_metadata({
                    "last_login": datetime.now(timezone.utc).isoformat(),
                    "is_active": True
                })
                
                logger.debug(f"User authenticated: {self.email_address} (Type: {self.user_type})")
                
                # Handle post-login redirect
                if self.redirect_after_login:
                    redirect_url = self.redirect_after_login
                    self.redirect_after_login = None
                    return rx.redirect(redirect_url)
                    
            else:
                # User is not authenticated - set to guest state
                logger.debug("User not authenticated, setting guest state")
                await self._set_guest_state()
                
                # Save current page for post-login redirect
                if hasattr(self.router, 'page') and self.router.page:
                    self.redirect_after_login = self.router.page.raw_path

        except Exception as e:
            logger.error("Error in sync_auth_state: %s", e, exc_info=True)
            # Fallback to guest state on any error
            await self._set_guest_state()
            self.redirect_after_login = None
            raise Exception("Critical error occurred while handling authentication state.") from e
    
    async def _set_guest_state(self):
        """Set the user state to guest mode."""
        # Reset all user fields to default/empty values
        self.reset()
        
        # Set guest-specific values
        self.user_type = UserType.GUEST.value
        self.email_address = ""
        self.first_name = ""
        self.last_name = ""
        self.username = ""
        self.clerk_id = ""
        self.is_active = False
        self.subscription_status = "free"
        self.subscription_plan = "basic"
        self.public_metadata = {}
        self.private_metadata = {}
        self.settings = {}
        self.user_collections = {}
    
    @rx.event
    async def initialize_new_user_metadata(self):
        """Initialize metadata for a newly registered user."""
        try:
            # Set default public metadata
            default_public_metadata = {
                "subscription_status": "free",
                "subscription_plan": "basic",
                "settings": {
                    "theme": "light",
                    "notifications": True,
                    "language": "en"
                }
            }
            
            # Set default private metadata
            default_private_metadata = {
                "user_collections": {},
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "last_login": datetime.now(timezone.utc).isoformat()
            }
            
            # Update metadata in Clerk
            await self.update_public_metadata(default_public_metadata)
            await self.update_private_metadata(default_private_metadata)
            
            logger.debug("Initialized metadata for new user")
            
        except Exception as e:
            logger.error(f"Error initializing new user metadata: {e}")
    
    @rx.event
    async def update_user_profile(self, profile_data: Dict[str, Any]):
        """Update user profile information in public metadata.
        
        Args:
            profile_data: Dictionary containing profile updates
        """
        try:
            # Extract settings if provided
            if "settings" in profile_data:
                current_settings = self.settings.copy()
                current_settings.update(profile_data["settings"])
                profile_data["settings"] = current_settings
            
            await self.update_public_metadata(profile_data)
            logger.debug(f"Updated user profile: {list(profile_data.keys())}")
            
        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
            raise
    
    @rx.event 
    async def get_user_data(self) -> Dict[str, Any]:
        """Get complete user data as a dictionary.
        
        Returns:
            Dictionary containing all user information
        """
        return {
            "clerk_id": self.clerk_id,
            "email_address": self.email_address,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "username": self.username,
            "user_type": self.user_type,
            "subscription_status": self.subscription_status,
            "subscription_plan": self.subscription_plan,
            "is_active": self.is_active,
            "avatar_url": self.avatar_url,
            "settings": self.settings,
            "user_collections": self.user_collections,
            "public_metadata": self.public_metadata,
            "private_metadata": self.private_metadata
        }