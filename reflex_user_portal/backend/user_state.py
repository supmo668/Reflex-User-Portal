"""User state management."""
import reflex as rx
from sqlmodel import Session, select, desc, asc, or_
import reflex_clerk as clerk
from datetime import datetime
from typing import Optional

from reflex_user_portal.config import ADMIN_USER_EMAIL
from reflex_user_portal.models.user import User, UserType
from reflex_user_portal.models.database import engine


class UserState(rx.State):
    """User state for the application."""
    
    # User state
    current_user: Optional[User] = None

    # Filtering and sorting state
    search_value: str = ""
    sort_value: str = ""
    sort_direction: str = "asc"

    # Pagination state
    total_items: int = 0
    offset: int = 0
    limit: int = 10

    # Users list
    users: list[User] = []

    @rx.var(cache=True)
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return rx.cond(
            clerk.ClerkState.is_signed_in, True, False)

    @rx.var
    def is_admin(self) -> bool:
        """Check if current user is admin by primary email address."""
        return rx.cond(
            self.is_authenticated,
            clerk.ClerkState.user.user_type == UserType.ADMIN, False )

    @rx.var
    def check_user_change(self) -> bool:
        """Check if user has changed."""
        return rx.cond(clerk.ClerkState.user.id != self.current_user.id, True, False) if self.current_user else False

    @rx.var(cache=True)
    def page_number(self) -> int:
        """Get current page number."""
        return (self.offset // self.limit) + 1

    @rx.var(cache=True)
    def total_pages(self) -> int:
        """Get total number of pages."""
        return max(1, (self.total_items + self.limit - 1) // self.limit)

    @rx.event
    async def sync_auth_state(self):
        """Update user state based on Clerk authentication state."""
        if self.check_user_change:
            await self.handle_sign_in()
        
    
    @rx.event
    async def handle_sign_in(self):
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

    @rx.event
    async def load_users(self):
        """Load users with current pagination, sorting, and filtering."""
        try:
            with rx.session() as session:
                query = select(User)

                # Apply search filter if present
                if self.search_value:
                    search = f"%{self.search_value.lower()}%"
                    query = query.where(
                        or_(
                            User.email.ilike(search),
                            User.first_name.ilike(search),
                            User.last_name.ilike(search)
                        )
                    )

                # Apply sorting
                if self.sort_value:
                    sort_column = getattr(User, self.sort_value)
                    if self.sort_direction == "desc":
                        query = query.order_by(desc(sort_column))
                    else:
                        query = query.order_by(asc(sort_column))

                # Get total count for pagination
                self.total_items = session.exec(
                    select(rx.sql.func.count()).select_from(query.subquery())
                ).one()

                # Apply pagination
                query = query.offset(self.offset).limit(self.limit)
                
                # Execute query
                self.users = session.exec(query).all()

        except Exception as e:
            print(f"Error loading users: {e}")
            self.users = []

    @rx.event
    async def prev_page(self):
        """Go to previous page."""
        self.offset = max(self.offset - self.limit, 0)
        yield self.load_users()

    @rx.event
    async def next_page(self):
        """Go to next page."""
        if self.offset + self.limit < self.total_items:
            self.offset += self.limit
        yield self.load_users()

    @rx.event
    async def sort_values(self, value: str):
        """Sort users by the specified column.
        
        Args:
            value: The column to sort by.
        """
        if self.sort_value == value:
            # Toggle direction if same column
            self.sort_direction = "desc" if self.sort_direction == "asc" else "asc"
        else:
            self.sort_value = value
            self.sort_direction = "asc"
        
        # Reset pagination when sort changes
        self.offset = 0
        yield self.load_users()

    @rx.event
    async def filter_values(self, value: str):
        """Filter users by search value.
        
        Args:
            value: The search string to filter by.
        """
        self.search_value = value
        # Reset pagination when filter changes
        self.offset = 0
        yield self.load_users()
