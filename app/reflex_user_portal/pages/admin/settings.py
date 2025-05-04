"""The settings page."""

import reflex as rx
import reflex_clerk as clerk

from ...templates import portal_template

from ... import styles

from ...components.admin_api_panel.navbar import render_navbar as render_api_navbar
from ...components.admin_api_panel.output import render_output
from ...components.admin_api_panel.query import render_query_component
from ...backend.states.admin.admin_api_panel_state import QueryAPI, QueryState


@portal_template(
    route="/admin/settings",
    title="Admin Config",
    on_load=[QueryAPI.ensure_defaults]
)
def admin_settings() -> rx.Component:
    """The settings page.

    Returns:
        The UI for the settings page.

    """
    return rx.vstack(
        render_api_navbar(),
        rx.hstack(
            render_query_component(),
            # for row entry viewing and editing
            render_output(),
            width="100%",
            spacing="2",
            padding="2em 1em",
            style={
                "margin_left": ["0", "0", styles.SIDEBAR_WIDTH],  # Responsive margin for sidebar
                "max_width": f"calc(100vw - {styles.SIDEBAR_WIDTH})",  # Prevent overflow under sidebar
                "box_sizing": "border-box",
            },
        ),
        rx.button(
            "Initialize Defaults",
            size="2",
            on_click=QueryAPI.init_defaults_and_refresh,
            cursor="pointer"
        ),
        align_items="center",  # Center children inside vstack=
        spacing="4",
        width="100%",
    )
