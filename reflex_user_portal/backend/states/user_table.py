"""Table state for managing user data."""
from typing import List

import reflex as rx
from sqlmodel import select, func, asc, desc, or_
from datetime import datetime, timezone

from reflex_user_portal.models.user import User
from reflex_user_portal.utils.logger import get_logger

logger = get_logger(__name__)


class TableState(rx.State):
    """Table state for managing user data."""
    
    users: List[User] = []
    total_items: int = 0
    offset: int = 0
    limit: int = 12  # Number of rows per page
    
    # Sorting and filtering
    sort_value: str = ""
    sort_reverse: bool = False
    search_value: str = ""
    
    # Current user for datetime formatting
    _current_user: User = None
    
    @rx.var(cache=True)
    def filtered_sorted_users(self) -> List[User]:
        """Get filtered and sorted users."""
        logger.debug("Filtering and sorting users")
        try:
            with rx.session() as session:
                query = select(User)
                
                # Apply search filter
                if self.search_value:
                    search = f"%{self.search_value.lower()}%"
                    query = query.where(
                        or_(
                            User.email.ilike(search),
                            User.first_name.ilike(search),
                            User.last_name.ilike(search),
                            User.user_type.ilike(search)
                        )
                    )
                
                # Apply sorting
                if self.sort_value:
                    sort_column = getattr(User, self.sort_value)
                    query = query.order_by(
                        desc(sort_column) if self.sort_reverse else asc(sort_column)
                    )
                
                # Execute query
                users = session.exec(query).all()
                logger.debug(f"Found {len(users)} users after filtering and sorting")
                return users
        except Exception as e:
            logger.error(f"Error filtering and sorting users: {e}", exc_info=True)
            return []

    @rx.var(cache=True)
    def page_number(self) -> int:
        """Get current page number."""
        return (self.offset // self.limit) + 1

    @rx.var(cache=True)
    def total_pages(self) -> int:
        """Get total number of pages."""
        return (self.total_items // self.limit) + (
            1 if self.total_items % self.limit else 1
        )
        
    @rx.var(cache=True)
    def get_current_page(self) -> List[User]:
        """Get users for current page."""
        users = self.filtered_sorted_users
        start_index = self.offset
        end_index = start_index + self.limit
        return users[start_index:end_index]

    def _format_datetime(self, dt: datetime | None) -> str:
        """Format datetime for display."""
        if not dt:
            return "Never"
        return dt.strftime("%Y-%m-%d %H:%M")

    def set_current_user(self, user: User) -> None:
        """Set current user for datetime formatting."""
        self._current_user = user

    @rx.var
    def created_at(self) -> str:
        """Get formatted created_at date."""
        if not self._current_user:
            return "Never"
        return self._format_datetime(self._current_user.created_at)

    @rx.var
    def last_login(self) -> str:
        """Get formatted last_login date."""
        if not self._current_user:
            return "Never"
        return self._format_datetime(self._current_user.last_login)
        
    def first_page(self):
        """Go to first page."""
        logger.debug("Moving to first page")
        self.offset = 0

    def last_page(self):
        """Go to last page."""
        logger.debug("Moving to last page")
        self.offset = (self.total_pages - 1) * self.limit

    def _get_total_table_entries(self, session) -> None:
        """Return the total number of items in the User table."""
        query = select(func.count(User.id))
        
        # Apply search filter if search value exists
        if self.search_value:
            search_value = f"%{self.search_value.lower()}%"
            query = query.where(
                or_(
                    User.first_name.ilike(search_value),
                    User.last_name.ilike(search_value),
                    User.email.ilike(search_value),
                )
            )
            
        self.total_table_entries = session.exec(query).one()

    @rx.event
    async def load_users(self):
        """Load all users."""
        logger.info("Loading all users")
        try:
            with rx.session() as session:
                query = select(User)
                self.users = session.exec(query).all()
                self.total_items = len(self.users)
                logger.info(f"Successfully loaded {self.total_items} users")
        except Exception as e:
            logger.error(f"Failed to load users: {e}", exc_info=True)
            self.users = []
            self.total_items = 0
            
    @rx.event
    def prev_page(self):
        """Go to previous page."""
        logger.debug("Moving to previous page")
        if self.page_number > 1:
            self.offset -= self.limit

    @rx.event
    def next_page(self):
        """Go to next page."""
        logger.debug("Moving to next page")
        if self.page_number < self.total_pages:
            self.offset += self.limit

    def toggle_sort(self):
        """Toggle sort direction."""
        logger.debug(f"Toggling sort direction from {self.sort_reverse}")
        self.sort_reverse = not self.sort_reverse

    def set_sort_value(self, value: str):
        """Set the sort column."""
        logger.debug(f"Setting sort value to {value}")
        self.sort_value = value

    def set_search_value(self, value: str):
        """Set the search value."""
        logger.debug(f"Setting search value to {value}")
        self.search_value = value
        self.offset = 0  # Reset to first page
