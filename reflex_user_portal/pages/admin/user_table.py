"""Admin user table page."""

import reflex as rx
import reflex_clerk as clerk

from reflex_user_portal.templates.portal import portal_template

from reflex_user_portal.backend.states.admin.user_table import TableState
from reflex_user_portal.models.admin.user import User
from reflex_user_portal.utils.logger import get_logger

logger = get_logger(__name__)

def _header_cell(text: str, icon: str) -> rx.Component:
    """Create a header cell with icon and text.

    Args:
        text: Header text
        icon: Icon name

    Returns:
        Header cell component
    """
    return rx.table.column_header_cell(
        rx.hstack(
            rx.icon(icon, size=18),
            rx.text(text),
            align="center",
            spacing="2",
        ),
    )


def _show_user(user: User, index: int) -> rx.Component:
    """Show a user in the table with alternating row colors.

    Args:
        user: The user to show
        index: Row index for alternating colors

    Returns:
        Table row component
    """
    try:        
        bg_color = rx.cond(
            index % 2 == 0,
            rx.color("gray", 1),
            rx.color("accent", 2),
        )
        hover_color = rx.cond(
            index % 2 == 0,
            rx.color("gray", 3),
            rx.color("accent", 3),
        )
        
        # Format dates using rx.text to avoid state var issues
        created_at = rx.text(
            rx.cond(
                user.created_at != None,
                user.created_at,
                "Never"
            )
        )
        
        last_login = rx.text(
            rx.cond(
                user.last_login != None,
                user.last_login,
                "Never"
            )
        )
        
        return rx.table.row(
            rx.table.row_header_cell(rx.text(user.full_name)),
            rx.table.cell(rx.text(user.email)),
            rx.table.cell(rx.text(user.user_type)),
            rx.table.cell(created_at),
            rx.table.cell(last_login),
            style={"_hover": {"bg": hover_color}, "bg": bg_color},
            align="center",
        )
    except Exception as e:
        logger.error(f"Error rendering user row: {e}", exc_info=True)
        # Return a fallback row with error indication
        return rx.table.row(
            rx.table.row_header_cell("Error"),
            rx.table.cell("Error loading user data"),
            rx.table.cell(""),
            rx.table.cell(""),
            rx.table.cell(""),
            style={"color": "red"},
            align="center",
        )

def _pagination_view() -> rx.Component:
    """Create pagination controls.

    Returns:
        Pagination component
    """
    return rx.hstack(
        rx.text(
            "Page ",
            rx.code(TableState.page_number),
            f" of {TableState.total_pages}",
            justify="end",
        ),
        rx.hstack(
            rx.icon_button(
                rx.icon("chevrons-left", size=18),
                on_click=TableState.first_page,
                opacity=rx.cond(TableState.page_number == 1, 0.6, 1),
                color_scheme=rx.cond(TableState.page_number == 1, "gray", "accent"),
                variant="soft",
            ),
            rx.icon_button(
                rx.icon("chevron-left", size=18),
                on_click=TableState.prev_page,
                opacity=rx.cond(TableState.page_number == 1, 0.6, 1),
                color_scheme=rx.cond(TableState.page_number == 1, "gray", "accent"),
                variant="soft",
            ),
            rx.icon_button(
                rx.icon("chevron-right", size=18),
                on_click=TableState.next_page,
                opacity=rx.cond(
                    TableState.page_number == TableState.total_pages, 0.6, 1
                ),
                color_scheme=rx.cond(
                    TableState.page_number == TableState.total_pages,
                    "gray",
                    "accent",
                ),
                variant="soft",
            ),
            rx.icon_button(
                rx.icon("chevrons-right", size=18),
                on_click=TableState.last_page,
                opacity=rx.cond(
                    TableState.page_number == TableState.total_pages, 0.6, 1
                ),
                color_scheme=rx.cond(
                    TableState.page_number == TableState.total_pages,
                    "gray",
                    "accent",
                ),
                variant="soft",
            ),
            align="center",
            spacing="2",
            justify="end",
        ),
        spacing="5",
        margin_top="1em",
        align="center",
        width="100%",
        justify="end",
    )


def users_table_content() -> rx.Component:
    """The users admin page.

    Returns:
        The page component
    """
    return rx.box(
        rx.heading("User Management", size="3", margin_bottom="4"),
        rx.flex(
            rx.flex(
                rx.cond(
                    TableState.sort_reverse,
                    rx.icon(
                        "arrow-down-z-a",
                        size=28,
                        stroke_width=1.5,
                        cursor="pointer",
                        flex_shrink="0",
                        on_click=TableState.toggle_sort,
                    ),
                    rx.icon(
                        "arrow-down-a-z",
                        size=28,
                        stroke_width=1.5,
                        cursor="pointer",
                        flex_shrink="0",
                        on_click=TableState.toggle_sort,
                    ),
                ),
                rx.select(
                    [
                        "email",
                        "first_name",
                        "last_name",
                        "user_type",
                        "created_at",
                        "last_login",
                    ],
                    placeholder="Sort By: Name",
                    size="3",
                    on_change=TableState.set_sort_value,
                ),
                rx.input(
                    rx.input.slot(rx.icon("search")),
                    rx.input.slot(
                        rx.icon("x"),
                        justify="end",
                        cursor="pointer",
                        on_click=TableState.setvar("search_value", ""),
                        display=rx.cond(TableState.search_value, "flex", "none"),
                    ),
                    value=TableState.search_value,
                    placeholder="Search users...",
                    size="3",
                    max_width=["150px", "150px", "200px", "250px"],
                    width="100%",
                    variant="surface",
                    color_scheme="gray",
                    on_change=TableState.set_search_value,
                ),
                align="center",
                justify="end",
                spacing="3",
            ),
            spacing="3",
            justify="between",
            wrap="wrap",
            width="100%",
            padding_bottom="1em",
        ),
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    _header_cell("Name", "user"),
                    _header_cell("Email", "mail"),
                    _header_cell("Role", "shield"),
                    _header_cell("Created", "calendar"),
                    _header_cell("Last Login", "clock"),
                ),
            ),
            rx.table.body(
                rx.foreach(
                    TableState.get_current_page,
                    lambda user, index: _show_user(user, index),
                )
            ),
            variant="surface",
            size="3",
            width="100%",
        ),
        _pagination_view(),
        width="100%",
        on_mount=TableState.load_users,
    )


@portal_template(route="/admin/users", title="User Management")
def users_table() -> rx.Component:
    """The users admin page.

    Returns:
        The page component.
    """
    page_content = clerk.protect(users_table_content())
    return page_content
