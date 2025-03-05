"""Admin user table page."""

import reflex as rx
from datetime import datetime

from reflex_user_portal.backend.table_state import TableState
from reflex_user_portal.models.user import User
from reflex_user_portal.templates.template import template

def format_datetime(dt: datetime) -> str:
    """Format a datetime object into a string.

    Args:
        dt: The datetime to format.

    Returns:
        A formatted string.
    """
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def show_user(user: User) -> rx.Component:
    """Show a user in the table.

    Args:
        user: The user to show.

    Returns:
        A table row component.
    """
    return rx.table.row(
        rx.table.cell(user.full_name),
        rx.table.cell(user.email),
        rx.table.cell(str(user.user_type)),
        rx.table.cell(
            rx.cond(
                user.last_login,
                user.last_login,
                "Never"
            )
        ),
    )


@template(route="/admin/users", title="User Management")
def users_table() -> rx.Component:
    """The users admin page.

    Returns:
        The page component.
    """
    return  rx.vstack(
                rx.heading("User Management", size="3"),
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
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Name"),
                            rx.table.column_header_cell("Email"),
                            rx.table.column_header_cell("Role"),
                            rx.table.column_header_cell("Last Login"),
                        ),
                    ),
                    rx.table.body(
                        rx.foreach(
                            TableState.users,
                            show_user,
                        )
                    ),
                    on_mount=TableState.load_users,
                    width="100%",
                ),
                rx.hstack(
                    rx.button(
                        "Prev",
                        on_click=TableState.prev_page,
                    ),
                    rx.text(
                        f"Page {TableState.page_number} / {TableState.total_pages}"
                    ),
                    rx.button(
                        "Next",
                        on_click=TableState.next_page,
                    ),
                    padding="4",
                    justify="center",
                ),
                width="100%",
                spacing="4",
            )
