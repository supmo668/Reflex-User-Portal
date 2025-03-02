"""Table view component."""
import reflex as rx

from reflex_user_portal.models.user import User
from reflex_user_portal.backend.table_state import TableState


def show_user(user: User) -> rx.Component:
    """Show a user in a table row."""
    return rx.table.row(
        rx.table.cell(user.full_name),
        rx.table.cell(user.email),
        rx.table.cell(user.user_type),
        rx.table.cell(rx.cond(user.is_active, "Yes", "No")),
        rx.table.cell(rx.cond(
            user.created_at,
            lambda dt: dt.strftime("%Y-%m-%d %H:%M"),
            "Never"
        )),
        rx.table.cell(rx.cond(
            user.last_login,
            lambda dt: dt.strftime("%Y-%m-%d %H:%M"),
            "Never"
        )),
    )


def main_table() -> rx.Component:
    """Main table component with pagination."""
    return rx.vstack(
        # Search and sort controls
        rx.hstack(
            rx.select(
                ["first_name", "last_name", "email", "user_type", "created_at"],
                placeholder="Sort by...",
                on_change=TableState.sort_values,
                value=TableState.sort_value,
            ),
            rx.input(
                placeholder="Search users...",
                on_change=TableState.filter_values,
                value=TableState.search_value,
                width="300px",
            ),
            width="100%",
            justify="between",
            padding="4",
        ),
        
        # Table
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("Name"),
                    rx.table.column_header_cell("Email"),
                    rx.table.column_header_cell("Role"),
                    rx.table.column_header_cell("Active"),
                    rx.table.column_header_cell("Created"),
                    rx.table.column_header_cell("Last Login"),
                ),
            ),
            rx.table.body(
                rx.foreach(
                    TableState.users,
                    show_user,
                ),
            ),
            on_mount=TableState.load_users,
            width="100%",
        ),
        
        # Pagination controls
        rx.hstack(
            rx.button(
                "Previous",
                on_click=TableState.prev_page,
                is_disabled=lambda: TableState.page_number == 1,
            ),
            rx.text(
                f"Page {TableState.page_number} / {TableState.total_pages}"
            ),
            rx.button(
                "Next",
                on_click=TableState.next_page,
                is_disabled=lambda: TableState.page_number >= TableState.total_pages,
            ),
            padding="4",
            justify="center",
        ),
        width="100%",
        spacing="4",
    )
