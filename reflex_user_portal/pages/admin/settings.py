"""The settings page."""

import reflex as rx
import reflex_clerk as clerk

from reflex_user_portal.templates import template

    

from reflex_user_portal.components.api_admin_panel.navbar import render_navbar
from reflex_user_portal.components.api_admin_panel.output import render_output
from reflex_user_portal.components.api_admin_panel.query import render_query_component
from reflex_user_portal.backend.api_admin_dashboard.queries import QueryAPI


@template(route="/admin/settings", title="Admin Config", on_load=QueryAPI.run_get_request)
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
    )
