"""Table state for managing user data."""
import reflex as rx
from sqlmodel import select, func, asc, desc, or_
from datetime import datetime, timezone

from reflex_user_portal.models.user import User
from reflex_user_portal.utils.logger import get_logger

logger = get_logger(__name__)


class TableState(rx.State):
    """Table state for managing user data."""
    
    users: list[User] = []
    total_table_entries: int = 0
    offset: int = 0
    limit: int = 3  # Smaller page size like the example
    
    # Sorting and filtering
    sort_value: str = ""
    sort_reverse: bool = False
    search_value: str = ""
    
    # Current user for datetime formatting
    _current_user: User = None

    @rx.var(cache=True)
    def page_number(self) -> int:
        """Get current page number."""
        return (
            (self.offset // self.limit)
            + 1
            + (1 if self.offset % self.limit else 0)
        )

    @rx.var(cache=True)
    def total_pages(self) -> int:
        """Get total number of pages."""
        return self.total_table_entries // self.limit + (
            1 if self.total_table_entries % self.limit else 0
        )

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
                self.total_table_entries = session.exec(
                    select(rx.sql.func.count()).select_from(query.subquery())
                ).one()

                # Apply pagination
                query = query.offset(self.offset).limit(self.limit)
                
                # Execute query
                self.users = session.exec(query).all()

        except Exception as e:
            logger.error(f"Failed to load users: {e}", exc_info=True)
            self.users = []
            
    @rx.event
    def prev_page(self):
        """Go to previous page."""
        self.offset = max(self.offset - self.limit, 0)
        self.load_entries()

    @rx.event
    def next_page(self):
        """Go to next page."""
        if self.offset + self.limit < self.total_table_entries:
            self.offset += self.limit
        self.load_entries()

    @rx.event
    def sort_values(self, value: str):
        """Sort the table by the given column."""
        if self.sort_value == value:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_value = value
            self.sort_reverse = False
        self.load_entries()

    @rx.event
    def filter_values(self, value: str):
        """Filter the table by the search value."""
        self.search_value = value
        self.offset = 0  # Reset to first page
        self.load_entries()
