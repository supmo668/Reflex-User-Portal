"""User state management."""
import os
from datetime import datetime
import reflex as rx
import reflex_clerk as clerk
from sqlmodel import Session, select

from reflex_user_portal.config import ADMIN_USER_EMAIL
from reflex_user_portal.models.user import User, UserType
from reflex_user_portal.models.database import engine


class UserState(rx.State):
    """The user state."""
    
    current_user: User | None = None
    users: list[User] = []
    is_signed_in: bool = False
    display_name: str = "Guest"
    avatar_url: str = ""

    def on_load(self) -> None:
        """Initialize state when component loads."""
        self.is_signed_in = clerk.ClerkState.is_signed_in
        self.get_or_create_user()
        self.update_user_info()

    def update_user_info(self) -> None:
        """Update user display info."""
        if not self.is_signed_in:
            self.display_name = "Guest"
            self.avatar_url = ""
            return

        if self.current_user:
            self.display_name = self.current_user.full_name
            self.avatar_url = self.current_user.avatar_url or ""
        else:
            self.display_name = "Guest"
            self.avatar_url = ""

    def get_or_create_user(self) -> None:
        """Get or create user from Clerk data."""
        try:
            with Session(engine) as session:
                # Check if Clerk user exists
                if clerk.ClerkState.user is None:
                    self.current_user = None
                    return

                # Get user by clerk ID
                clerk_id = clerk.ClerkState.user.id
                user = session.exec(
                    select(User).where(User.clerk_id == clerk_id)
                ).first()
                
                if not user:
                    # Check if user should be admin based on email
                    if not clerk.ClerkState.user.email_addresses:
                        self.current_user = None
                        return
                        
                    user_email = clerk.ClerkState.user.email_addresses[0].email_address
                    is_admin = user_email == ADMIN_USER_EMAIL
                    
                    # Create new user
                    user = User(
                        email=user_email,
                        clerk_id=clerk_id,
                        user_type=UserType.ADMIN if is_admin else UserType.USER,
                        first_name=clerk.ClerkState.user.first_name or "",
                        last_name=clerk.ClerkState.user.last_name or "",
                        created_at=datetime.utcnow(),
                        last_login=datetime.utcnow(),
                    )
                    
                    session.add(user)
                    session.commit()
                    session.refresh(user)
                else:
                    # Update last login time
                    user.last_login = datetime.utcnow()
                    session.add(user)
                    session.commit()
                    session.refresh(user)
                
                self.current_user = user
        except Exception as e:
            print(f"Error getting/creating user: {e}")
            self.current_user = None

    def is_admin(self) -> bool:
        """Check if current user is admin."""
        try:
            with Session(engine) as session:
                # Get user by clerk ID
                if clerk.ClerkState.user is None:
                    return False
                clerk_id = clerk.ClerkState.user.id
                user = session.exec(
                    select(User).where(User.clerk_id == clerk_id)
                ).first()
                return user is not None and user.user_type == UserType.ADMIN
        except:
            return False

    @rx.var
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return self.current_user is not None

    @rx.var
    def user_name(self) -> str:
        """Get user's full name."""
        if self.current_user:
            return self.current_user.full_name
        return "Guest"

    def load_users(self) -> None:
        """Get all users from the database."""
        try:
            if not self.is_admin():
                self.users = []
                return
                
            with Session(engine) as session:
                self.users = session.exec(select(User)).all()
        except Exception as e:
            print(f"Error loading users: {e}")
            self.users = []
