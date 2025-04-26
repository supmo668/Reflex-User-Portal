"""Common components used between pages in the app."""
from typing import Callable, List, Union
import reflex as rx

from ...backend.states.admin.admin_api_panel_state import QueryAPI


def render_field(field_name: rx.Var, field_value: rx.Var) -> rx.Component:
    """Render an input field based on field type.
    
    Args:
        field_name: Name of the field as a Var
        field_value: Value of the field as a Var
        
    Returns:
        Input component
    """
    # fields to be read-only and not displayed in the drawer
    readonly_fields = rx.Var.create(["id", "created_at", "updated_at"])
    
    return rx.vstack(
        rx.text(field_name, weight="bold"),
        rx.cond(
            field_name == "configuration",
            rx.text_area(
                value=field_value,
                width="100%",
                on_change=lambda value: QueryAPI.update_data(value, field_name),
                placeholder=f"{field_name}",
                disabled=readonly_fields.contains(field_name),
                min_height="200px",
            ),
            rx.input(
                value=field_value,
                width="100%",
                on_change=lambda value: QueryAPI.update_data(value, field_name),
                placeholder=f"{field_name}",
                disabled=readonly_fields.contains(field_name),
            ),
        ),
        width="100%",
        spacing="2",
    )


def render_entry_fields() -> rx.Component:
    """Render all fields for the selected entry."""
    return rx.vstack(
        rx.foreach(
            QueryAPI.selected_entry.items(),
            lambda item: render_field(
                rx.Var.create(item[0]),
                rx.Var.create(item[1])
            )
        ),
        width="100%",
        spacing="4",
    )


def render_drawer_buttons(name: str, color: str, function: Union[Callable, List[Callable]]) -> rx.Component:
    """Render a drawer action button.
    
    Args:
        name: Button text
        color: Color scheme
        function: Click handler function
        
    Returns:
        Button component
    """
    return rx.badge(
        rx.text(name, width="100%", text_align="center"),
        color_scheme=color,
        on_click=function,
        variant="surface",
        padding="0.75em 1.25em",
        width="100%",
        cursor="pointer",
    )


def render_drawer() -> rx.Component:
    """Render the drawer component."""
    return rx.drawer.root(
        rx.drawer.overlay(z_index="5"),
        rx.drawer.portal(
            rx.drawer.content(
                rx.vstack(
                    # Show error message if present
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
                    # Entry fields
                    render_entry_fields(),
                    # Action buttons
                    rx.vstack(
                        render_drawer_buttons(
                            "Commit", "grass", 
                            [QueryAPI.commit_changes, QueryAPI.refresh_table_data]
                        ),
                        render_drawer_buttons("Close", "ruby", QueryAPI.delta_drawer),
                        padding="1em 0.5em",
                        width="inherit",
                    ),
                    bg=rx.color_mode_cond("#faf9fb", "#1a181a"),
                    height="100%",
                    width="100%",
                    padding="1.25em",
                ),
                top="auto",
                left="auto",
                height="100%",
                width="30em",
                on_interact_outside=QueryAPI.delta_drawer,
                role="dialog",
                aria_label="Edit entry",
            ),
        ),
        handle_only=True,  # Add this line
        direction="right",
        open=QueryAPI.is_open,
    )
