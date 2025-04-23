import reflex as rx
import json
from datetime import datetime
from typing import Any, Dict, Tuple

from ...components.admin_api_panel.drawer import render_drawer
from ...backend.states.admin.admin_api_panel_state import QueryAPI


def create_table_header(title: rx.Var) -> rx.Component:
    """Create a table header cell.
    
    Args:
        title: Column title
        
    Returns:
        Header cell component
    """
    return rx.table.column_header_cell(
        title,
        font_weight="bold",
        text_transform="capitalize",
    )

def create_query_rows(data: Dict[str, Any]) -> rx.Component:
    """Create a table row for the given data.
    
    Args:
        data: Row data dictionary with potentially nested values
        
    Returns:
        Table row component
    """
    def fill_rows_with_data(item: Tuple[str, Any]) -> rx.Component:
        """Create a table cell for a single field."""
        return rx.table.cell(
            item[1],  # Ensure we're passing a string
            on_click=lambda: QueryAPI.display_selected_row(data),
            cursor="pointer",
            title=f"Click to edit {item[0]}",
            role="button",
            aria_label=f"Edit {item[0]}",
            text_align="left",
            padding="2",
        )

    return rx.table.row(
        rx.foreach(
            data, fill_rows_with_data
        ),
        _hover={"bg": rx.color(color="gray", shade=4)},
        role="row",
    )


def create_pagination() -> rx.Component:
    """Create pagination controls.
    
    Returns:
        Pagination component
    """
    return rx.hstack(
        rx.hstack(
            rx.text("Entries per page", weight="bold"),
            rx.select(
                QueryAPI.limits,
                default_value="10",
                on_change=QueryAPI.delta_limit,
            ),
            align_items="center",
        ),
        rx.hstack(
            rx.text(
                f"Page {QueryAPI.current_page}/{QueryAPI.total_pages}",
                width="100px",
                weight="bold",
            ),
            rx.hstack(
                    rx.button(
                        rx.icon(tag="chevron-left"),
                        on_click=QueryAPI.previous,
                        is_disabled=QueryAPI.current_page <= 1,
                    ),
                    rx.button(
                        rx.icon(tag="chevron-right"), 
                        on_click=QueryAPI.next,
                        is_disabled=QueryAPI.current_page >= QueryAPI.total_pages,
                    ),
                    spacing="0",
                ),
            align_items="center",
            spacing="2",
        ),
        align_items="center",
        justify="between",
        width="100%",
        padding="4",
    )


def render_output() -> rx.Component:
    """Render the main output component."""
    return rx.center(
        rx.cond(
            QueryAPI.table_data,
            rx.vstack(
                # Error alert if needed
                rx.cond(
                    QueryAPI.show_error,
                    rx.alert_dialog.root(
                        rx.alert_dialog.content(
                            rx.alert_dialog.title("Error"),
                            rx.alert_dialog.description(QueryAPI.error_message),
                            rx.flex(
                                rx.alert_dialog.action(
                                    rx.button(
                                        "OK",
                                        on_click=QueryAPI.handle_error_ok,
                                    ),
                                ),
                                spacing="3",
                                justify="end",
                            ),
                        ),
                        open=QueryAPI.show_error,
                    ),
                ),
                # Drawer for editing
                render_drawer(),
                # Pagination controls
                create_pagination(),
                # Data table
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.foreach(
                                QueryAPI.table_headers, create_table_header)
                        ),
                    ),
                    rx.table.body(
                        rx.foreach(QueryAPI.paginated_data, create_query_rows)
                    ),
                    width="100%",
                    variant="surface",
                    size="1",
                ),
                rx.text(
                    "* Click a row to edit its contents.",
                    weight="bold",
                    size="1",
                    color="gray.500",
                ),
                width="100%",
                overflow="auto",
                padding="2em 2em",
                spacing="4",
            ),
            rx.vstack(
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.foreach(QueryAPI.table_headers, create_table_header)
                        ),
                    ),
                    rx.table.body(
                        rx.foreach(QueryAPI.paginated_data, create_query_rows)
                    ),
                    width="100%",
                    variant="surface",
                    size="1",
                ),
                padding="2em",
                spacing="4",
            ),
        ),
        flex="60%",
        bg=rx.color_mode_cond(
            "#faf9fb",
            "#1a181a",
        ),
        border_radius="10px",
        overflow="auto",
    )
