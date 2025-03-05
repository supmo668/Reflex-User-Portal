"""User state management."""
import reflex as rx
from sqlmodel import select
import reflex_clerk as clerk
from datetime import datetime
from typing import Optional

from reflex_user_portal.config import ADMIN_USER_EMAIL
from reflex_user_portal.models.user import User, UserType


class UserState(rx.State):
    """User state for the application."""
    
    # User state
    current_user: Optional[User] = None

    @rx.var
    def is_admin(self) -> bool:
        """Check if current user is admin by primary email address."""
        return self.current_user.user_type == UserType.ADMIN if self.current_user else False
    
    @rx.event
    async def sync_auth_state(self):
        """Handle user sign in.
        sync Clerk user info to internal user database 
        """
        try:
            with rx.session() as session:
                clerk_id = clerk.ClerkState.user.id
                user = session.exec(
                    select(User).where(User.clerk_id == clerk_id)
                ).first()

                if user is None:
                    await self._create_new_user(session)
                else:
                    await self._update_existing_user(session, user)
        except Exception as e:
            print(f"Error handling sign in: {e}")
            self.current_user = None

    async def _create_new_user(self, session) -> None:
        """Create a new user in the database."""
        if not clerk.ClerkState.user.email_addresses:
            self.current_user = None
            return

        user_email = clerk.ClerkState.user.primary_email_address_id
        is_admin = user_email == ADMIN_USER_EMAIL
        
        user = User(
            email=user_email,
            clerk_id=clerk.ClerkState.user.id,
            user_type=UserType.ADMIN if is_admin else UserType.USER,
            first_name=clerk.ClerkState.user.first_name or "",
            last_name=clerk.ClerkState.user.last_name or "",
            created_at=datetime.utcnow(),
            last_login=datetime.utcnow(),
        )
        
        session.add(user)
        session.commit()
        session.refresh(user)
        self.current_user = user

    async def _update_existing_user(self, session, user: User) -> None:
        """Update an existing user in the database."""
        user.first_name = clerk.ClerkState.user.first_name or user.first_name
        user.last_name = clerk.ClerkState.user.last_name or user.last_name
        user.last_login = datetime.utcnow()
        session.add(user)
        session.commit()
        session.refresh(user)
        self.current_user = user
