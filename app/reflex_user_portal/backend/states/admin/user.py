"""User state management."""
from datetime import datetime, timezone
from typing import Optional, Dict, Any

import reflex as rx
from sqlmodel import select
import reflex_clerk as clerk
from clerk_backend_api.models import User as ClerkUser

from app.config import ADMIN_USER_EMAILS
from app.models.admin.user import User, UserType, UserAttribute
from app.utils.logger import get_logger

logger = get_logger(__name__)


class UserBaseState(rx.State):
    """User state for the application."""
    
    # User state
    user: Optional[User] = None
    redirect_after_login: Optional[str] = None
    
    @rx.var
    async def is_admin(self) -> bool:
        """Check if current user is admin."""
        if self.user:
            return self.user.user_type == UserType.ADMIN
        return False
    
    @rx.var
    def admin_emails(self) -> list[str]:
        with rx.session() as session:
            return [
                user.email
                for user in session.exec(
                    User.select().where(User.user_type == UserType.ADMIN)
                ).all()
            ]
    
    async def get_or_create_guest(self) -> User:
        """Get or create guest user."""
        with rx.session() as session:
            # Find existing guest user
            user = session.exec(
                select(User).where(User.user_type == UserType.GUEST)
            ).first()
            if user is None:
                # Create new guest user with a generated email
                timestamp = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')
                user = User(
                    email=f"guest_{timestamp}@temp.com",  # Generate unique email
                    user_type=UserType.GUEST,
                    created_at=datetime.now(timezone.utc)
                )
                session.add(user)
                session.commit()
                session.refresh(user)
        return user
    
    async def get_or_create_user(self, clerk_user: ClerkUser = None) -> User:
        """Get or create user based on Clerk info."""
        if not clerk_user:
            clerk_state = await self.get_state(clerk.ClerkState)
            clerk_user = clerk_state.user
        with rx.session() as session:
            # Find existing user
            user = session.exec(
                select(User).where(User.clerk_id == clerk_user.id)
            ).first()
            
            if user is None:
                # Create new user
                user = User(
                    email=clerk_user.primary_email_address_id,
                    clerk_id=clerk_user.id,
                    first_name=clerk_user.first_name,
                    last_name=clerk_user.last_name,
                    created_at=datetime.now(timezone.utc)
                )
        # return local user 
        return user
                    

class UserAuthState(UserBaseState):
    """User authentication state management."""
    @rx.event
    async def sync_auth_state(self):
        """Handle user sign in.
        sync Clerk user info to internal user database. handle events on page load:
        - User signing in:
            - Create new user if not exists
            - Update user attributes (if exists)
            - handle redirect to pre sign-in
        - User signing out or browsing as guest(signed-out):
            - Reset user state as guest
            - save redirection url
        """
        # Fetch clerk state
        clerk_state = await self.get_state(clerk.ClerkState)
        logger.debug("Clerk state: %s", clerk_state.is_signed_in)
        try:
            if clerk_state.is_signed_in:
                user = await self.get_or_create_user(clerk_user=clerk_state.user)
                with rx.session() as session:
                    # Update user attributes
                    admin_emails = ADMIN_USER_EMAILS + [self.admin_emails]
                    user_email = clerk_state.user.email_addresses[0].email_address
                    user.user_type = UserType.ADMIN if user_email in admin_emails else UserType.USER
                    user.last_login = datetime.now(timezone.utc)
                    # commit changes
                    session.add(user)
                    session.commit()
                    session.refresh(user)
                    
                    # Store role and handle redirect
                    self.user = user
                    if self.redirect_after_login is not None:
                        redirect_url = self.redirect_after_login
                        # reset redirect
                        self.redirect_after_login = None
                        return rx.redirect(redirect_url)
            else:
                # Not signed in
                logger.debug("User is not signed in, setting guest user")
                self.user = await self.get_or_create_guest()
                self.redirect_after_login = self.router.page.raw_path

        except Exception as e:
            logger.error("Error handling auth state change: %s", e, exc_info=True)
            self.user = await self.get_or_create_guest()
            self.redirect_after_login = None
            raise Exception("Critical error occurred while handling authentication state.") from e

class UserAttributeState(UserBaseState):
    """State for managing user attributes and collections."""
    
    user_collections: Dict[str, Any] = {}
    
    @rx.var
    async def get_user_attribute(self) -> Optional[UserAttribute]:
        """Get current user's attribute record."""
        if not self.user:
            return None
            
        with rx.session() as session:
            return session.exec(
                select(UserAttribute).where(
                    UserAttribute.user_id == self.user.id
                )
            ).first()

    @rx.event
    async def init_user_collections(self):
        """Initialize user collections from database."""
        user_attr = await self.get_user_attribute
        if user_attr:
            self.user_collections = user_attr.user_collections

    @rx.event
    async def add_to_collection(self, collection_name: str, item: Any):
        """Add item to a specific collection."""
        if not self.user:
            return
            
        with rx.session() as session:
            user_attr = await self.get_user_attribute
            if not user_attr:
                # Create new user attribute record
                user_attr = UserAttribute(
                    user_id=self.user.id,
                    user_collections={collection_name: [item]}
                )
            else:
                # Update existing collections
                if collection_name not in user_attr.user_collections:
                    user_attr.user_collections[collection_name] = []
                user_attr.user_collections[collection_name].append(item)
            
            session.add(user_attr)
            session.commit()
            session.refresh(user_attr)
            self.user_collections = user_attr.user_collections

    @rx.event 
    async def remove_from_collection(self, collection_name: str, item: Any):
        """Remove item from a specific collection."""
        if not self.user:
            return
            
        with rx.session() as session:
            user_attr = await self.get_user_attribute
            if user_attr and collection_name in user_attr.user_collections:
                try:
                    user_attr.user_collections[collection_name].remove(item)
                    session.add(user_attr)
                    session.commit()
                    session.refresh(user_attr)
                    self.user_collections = user_attr.user_collections
                except ValueError:
                    # Item not in collection
                    pass

    @rx.event
    async def clear_collection(self, collection_name: str):
        """Clear all items from a specific collection."""
        if not self.user:
            return
            
        with rx.session() as session:
            user_attr = await self.get_user_attribute
            if user_attr and collection_name in user_attr.user_collections:
                user_attr.user_collections[collection_name] = []
                session.add(user_attr)
                session.commit()
                session.refresh(user_attr)
                self.user_collections = user_attr.user_collections