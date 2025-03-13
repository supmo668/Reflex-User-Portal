from __future__ import annotations

import os
from typing import Any

import reflex as rx
from reflex_user_portal.backend.states.admin_api_panel_state import QueryAPI, QueryState


def get_database_url() -> str:
    """Get the database URL from environment variables."""
    return os.getenv('SUPABASE_DB_URL', '')


def get_database_token() -> str:
    """Get the database token status."""
    return "*"*len(os.getenv('SUPABASE_DB_TOKEN')) if os.getenv('SUPABASE_DB_TOKEN') else ""



def form_request_item() -> rx.Component:
    """Render the database connection information form."""
    return rx.accordion.root(
        rx.accordion.item(
            header=rx.text("Database Connection", font_size="var(--chakra-fontSizes-sm)"),
            content=rx.vstack(
                rx.text(
                    "Database URL:",
                    font_size="0.9em",
                    color="gray.500"
                ),
                rx.input(
                    value=get_database_url(),
                    on_change=QueryState.update_db_url,
                    placeholder=get_database_url(), 
                    font_size="0.9em",
                    color="gray.500"
                ),
                rx.text(
                    "Token:",
                    font_size="0.9em",
                    color="gray.500"
                ),
                rx.input(
                    value=get_database_token(),
                    on_change=QueryState.update_db_key,
                    placeholder=get_database_token(), 
                    font_size="0.9em",
                    color="gray.500"
                ),
                rx.text(
                    f"Selected Table:{QueryAPI.current_table}",
                    font_size="0.9em",
                    color="gray.500"
                ),
                width="100%",
                align_items="start",
                spacing="2"
            ),
            value="connection",
        ),
        collapsible=True,
        width="100%",
    )


def render_pagination_controls() -> rx.Component:
    """Render pagination controls for table data."""
    return rx.hstack(
        rx.hstack(
            rx.text("Items per page:", font_size="0.9em", color="gray.500"),
            rx.select(
                QueryAPI.limits,
                default_value="10",
                on_change=QueryAPI.delta_limit,
                aria_label="Select number of items per page",
            ),
            spacing="2",
            align_items="center",
        ),
        rx.spacer(),
        rx.button(
            "Previous",
            on_click=QueryAPI.previous,
            is_disabled=QueryAPI.current_page <= 1,
            variant="surface",
            aria_label="Go to previous page",
        ),
        rx.text(
            f"Page {QueryAPI.current_page} of {QueryAPI.total_pages}",
            font_size="0.9em",
            color="gray.500",
            min_width="100px",
            text_align="center",
            aria_label=f"Current page {QueryAPI.current_page} of {QueryAPI.total_pages}",
        ),
        rx.button(
            "Next",
            on_click=QueryAPI.next,
            is_disabled=QueryAPI.current_page >= QueryAPI.total_pages,
            variant="surface",
            aria_label="Go to next page",
        ),
        width="100%",
        padding="1em",
        border_top=rx.color_mode_cond(
            "1px solid rgba(45, 45, 45, 0.05)",
            "1px solid rgba(45, 45, 45, 0.51)"
        ),
        align_items="center",
        role="navigation",
        aria_label="Table pagination",
    )

def render_query_form() -> rx.Component:
    """Render the query form with database connection info and pagination."""
    return rx.vstack(
        form_request_item(),
        render_pagination_controls(),
        width="100%",
        spacing="2",
        padding="0em 0.75em",
    )


def render_query_header() -> rx.Component:
    """Render the query header with table selector and refresh button."""
    return rx.hstack(
        rx.hstack(
            rx.select(
                QueryAPI.available_tables,
                width="200px",
                default_value="admin_config",
                on_change=QueryAPI.select_table,
                placeholder="Select a table"
            ),
            rx.text(
                QueryAPI.connection_status,
                font_size="1em",
                color=rx.cond(
                    QueryAPI.is_connected,
                    "green.500",
                    "orange.500"
                ),
                justify="center",
            ),
            width="100%",
            spacing="3",
            justify="center",
            align="center",
        ),
        rx.button(
            "Refresh", size="2", on_click=QueryAPI.refresh_table_data, cursor="pointer"
        ),
        width="100%",
        border_bottom=rx.color_mode_cond(
            "1px solid rgba(45, 45, 45, 0.05)", "1px solid rgba(45, 45, 45, 0.51)"
        ),
        padding="1em 0.75em",
        justify_content="end",
    )


def render_query_component() -> rx.Component:
    """Render the complete query component with header, form, and pagination."""
    return rx.vstack(
        render_query_header(),
        render_query_form(),
        flex=["100%", "100%", "100%", "100%", "30%"],
        display=QueryAPI.query_component_toggle,
        padding_bottom="0.75em",
        border_radius="10px",
        bg=rx.color_mode_cond(
            "#faf9fb",
            "#1a181a",
        ),
    )
