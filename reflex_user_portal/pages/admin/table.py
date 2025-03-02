"""Admin table page."""
import reflex as rx

from reflex_user_portal.templates import template
from reflex_user_portal.models.user import User
from reflex_user_portal.backend.table_state import TableState
from reflex_user_portal.backend.user_state import UserState


def show_user(user: User):
    """Show a user in a table row."""
    TableState.set_current_user(user)
    return rx.table.row(
        rx.table.cell(user.full_name),
        rx.table.cell(user.email),
        rx.table.cell(user.user_type),
        rx.table.cell(rx.cond(user.is_active, "Yes", "No")),
        rx.table.cell(TableState.created_at),
        rx.table.cell(TableState.last_login),
    )


@template(route="/admin/users", title="User Management")
def user_table() -> rx.Component:
    """User management table page."""
    if not UserState.is_admin():
        return rx.vstack(
            rx.heading("Access Denied", size="3"),
            rx.text("You do not have permission to view this page."),
            width="100%",
            spacing="4",
        )

    return rx.vstack(
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
                    rx.table.column_header_cell("Active"),
                    rx.table.column_header_cell("Created"),
                    rx.table.column_header_cell("Last Login"),
                ),
            ),
            rx.table.body(
                rx.foreach(
                    TableState.users,
                    show_user,
                )
            ),
            on_mount=TableState.load_entries,
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
