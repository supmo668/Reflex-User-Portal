"""The settings page."""

import reflex as rx
import reflex_clerk as clerk

from reflex_user_portal.templates import portal_template
from reflex_user_portal.views.color_picker import primary_color_picker, secondary_color_picker
from reflex_user_portal.views.radius_picker import radius_picker
from reflex_user_portal.views.scaling_picker import scaling_picker

@portal_template(route="/app-settings", title="App Settings")
def app_settings() -> rx.Component:
    """The settings page content.

    Returns:
        The UI for the settings page.
    """
    return rx.vstack(
        rx.heading("Settings", size="5"),
        # Primary color picker
        rx.vstack(
            rx.hstack(
                rx.icon("palette", color=rx.color("accent", 10)),
                rx.heading("Primary color", size="6"),
                align="center",
            ),
            primary_color_picker(),
            spacing="4",
            width="100%",
        ),
        # Secondary color picker
        rx.vstack(
            rx.hstack(
                rx.icon("blend", color=rx.color("gray", 11)),
                rx.heading("Secondary color", size="6"),
                align="center",
            ),
            secondary_color_picker(),
            spacing="4",
            width="100%",
        ),
        # Radius picker
        radius_picker(),
        # Scaling picker
        scaling_picker(),
        spacing="7",
        width="100%",
    )