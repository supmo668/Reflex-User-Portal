"""The settings page."""

import reflex as rx
import reflex_clerk as clerk

from ...templates import portal_template

    

from ...components.admin_api_panel.navbar import render_navbar
from ...components.admin_api_panel.output import render_output
from ...components.admin_api_panel.query import render_query_component
from ...backend.states.admin.admin_api_panel_state import QueryAPI, QueryState


@portal_template(route="/admin/settings", title="Admin Config", on_load=[QueryAPI.refresh_table_data])
def admin_settings() -> rx.Component:
    """The settings page.

    Returns:
        The UI for the settings page.

    """
    return rx.vstack(
        render_navbar(),
        rx.hstack(
            render_query_component(),
            render_output(),
            width="100%",
            display="flex",
            flex_wrap="wrap",
            spacing="6",
            padding="2em 1em",
        ),
        spacing="4",
        width="100%"
    )
