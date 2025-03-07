"""User state management."""
import reflex as rx
from sqlmodel import select
import reflex_clerk as clerk
from datetime import datetime, timezone
from typing import Optional

from reflex_user_portal.config import ADMIN_USER_EMAILS
from reflex_user_portal.models.user import User, UserType


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
    async def set_redirect(self):
        self.redirect_after_login = self.router.page.raw_path
        
    @rx.event
    async def sync_auth_state(self):
        """Handle user sign in.
        sync Clerk user info to internal user database.
        """
        # Fetch clerk state
        clerk_state = await self.get_state(clerk.ClerkState)
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
                        session.add(user)
                    
                    # Update user attributes
                    user.user_type = UserType.ADMIN if clerk_state.user.primary_email_address_id in ADMIN_USER_EMAILS else UserType.USER
                    user.last_login = datetime.now(timezone.utc)

                    # commit changes
                    session.commit()
                    session.refresh(user)
                    
                    # Store role and handle redirect
                    self.user_role = user.user_type.value
                    if self.redirect_after_login:
                        redirect_url = self.redirect_after_login
                        self.redirect_after_login = None
                        return rx.redirect(redirect_url)
            else:
                # Not signed in
                self.user_role = UserType.GUEST.value
                self.redirect_after_login = None
                return rx.redirect("/sign-in")

        except Exception as e:
            print(f"Error handling auth state change: {e}")
            self.user_role = UserType.GUEST.value
            self.redirect_after_login = None