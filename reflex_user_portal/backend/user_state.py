"""User state management."""
import reflex as rx
from sqlmodel import select
import reflex_clerk as clerk
from datetime import datetime, timezone
from typing import Optional

from reflex_user_portal.config import ADMIN_USER_EMAILS
from reflex_user_portal.models.user import User, UserType
from reflex_user_portal.utils.logger import get_logger

logger = get_logger(__name__)


class UserState(rx.State):
    """User state for the application."""
    
    # User state
    user_role: str = UserType.GUEST.value
    redirect_after_login: Optional[str] = None
    
    @rx.var
    async def is_admin(self) -> bool:
        """Check if current user is admin."""
        return self.user_role == UserType.ADMIN.value

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
        logger.debug(f"Clerk state: {clerk_state.is_signed_in}")
        try:
            if clerk_state.is_signed_in:
                with rx.session() as session:
                    # Find existing user
                    user = session.exec(
                        select(User).where(User.clerk_id == clerk_state.user.id)
                    ).first()
                    
                    if user is None:
                        # Create new user
                        user = User(
                            email=clerk_state.user.primary_email_address_id,
                            clerk_id=clerk_state.user.id,
                            first_name=clerk_state.user.first_name,
                            last_name=clerk_state.user.last_name,
                            created_at=datetime.now(timezone.utc)
                        )
                    
                    # Update user attributes
                    user.user_type = UserType.ADMIN if clerk_state.user.email_addresses[0].email_address in ADMIN_USER_EMAILS else UserType.USER
                    user.last_login = datetime.now(timezone.utc)
                    session.add(user)
                    # commit changes
                    session.commit()
                    session.refresh(user)
                    
                    # Store role and handle redirect
                    self.user_role = user.user_type.value
                    if self.redirect_after_login is not None:
                        redirect_url = self.redirect_after_login
                        # reset redirect
                        self.redirect_after_login = None
                        return rx.redirect(redirect_url)
            else:
                # Not signed in
                self.user_role = UserType.GUEST.value
                self.redirect_after_login = self.router.page.raw_path

        except Exception as e:
            logger.error(f"Error handling auth state change: {e}", exc_info=True)
            self.user_role = UserType.GUEST.value
            self.redirect_after_login = None