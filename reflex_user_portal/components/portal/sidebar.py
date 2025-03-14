"""Sidebar component for the app."""
import os
import reflex as rx

from reflex_user_portal import styles
from reflex_user_portal.backend.states.user_state import UserState
from reflex_user_portal.templates.template_config import NavItem, NAV_ITEMS

from reflex_user_portal.views.logo import logo

def sidebar_header() -> rx.Component:
    """Sidebar header.

    Returns:
        The sidebar header component.
    """
    return rx.hstack(
        logo(),
        rx.spacer(),
        align="center",
        width="100%",
        padding="4",
        height="64px",  # Match navbar height
    )


def sidebar_footer() -> rx.Component:
    """Sidebar footer.

    Returns:
        The sidebar footer component.
    """
    return rx.vstack(
        rx.divider(),
        rx.hstack(
            rx.link(
                rx.text("Site", size="3"),
                href=os.getenv("SITE_URL", "/"),
                color=styles.text_color,
                _hover={"color": styles.accent_text_color},
            ),
            rx.spacer(),
            rx.color_mode.button(
                style={
                    "opacity": "0.8", 
                    "scale": "0.95",
                    "_hover": {"opacity": 1},
                }
            ),
            width="100%",
            padding="4",
        ),
        width="100%",
        spacing="0",
    )


def sidebar_item(item: NavItem) -> rx.Component:
    """Create a sidebar item.

    Args:
        item: The navigation item configuration.

    Returns:
        The sidebar item component.
    """
    # Whether the item is active: currently selected or default page
    active = UserState.is_hydrated & (
        (rx.State.router.page.path == item.route.lower()) | (rx.State.router.page.path == "/overview") & (rx.State.router.page.path == "/")
    )

    return rx.cond(
        item.should_show(UserState),
        rx.link(
            rx.hstack(
                rx.icon(item.icon, size=18),
                rx.text(item.title, size="3"),
                width="100%",
                color=rx.cond(
                    active,
                    styles.accent_text_color,
                    styles.text_color,
                ),
                bg=rx.cond(
                    active,
                    styles.accent_bg_color,
                    "transparent",
                ),
                border_radius="lg",
                padding_x="3",
                padding_y="2",
                spacing="3",
                style={
                    "_hover": {
                        "background_color": rx.cond(
                            active,
                            styles.accent_bg_color,
                            styles.gray_bg_color,
                        ),
                        "color": rx.cond(
                            active,
                            styles.accent_text_color,
                            styles.text_color,
                        ),
                    }
                },
            ),
            href=item.route,
            width="100%",
        ),
    )


def sidebar() -> rx.Component:
    """The sidebar.

    Returns:
        The sidebar component.
    """
    return rx.flex(
        rx.vstack(
            sidebar_header(),
            rx.vstack(
                *[sidebar_item(item) for item in NAV_ITEMS],
                spacing="1",
                width="100%",
                overflow_y="auto",
                align_items="flex-start",
                padding="4",
            ),
            rx.spacer(),
            sidebar_footer(),
            justify="end",
            align="end",
            width=styles.sidebar_content_width,
            height="100dvh",
            padding="1em",
            spacing="0",
        ),
        display=["none"]*(len(NAV_ITEMS)-1)+ ["flex"],
        max_width=styles.sidebar_width,
        width="auto",
        height="100%",
        position="sticky",
        justify="end",
        top="0",
        left="0",
        flex="1",
        bg=rx.color("gray", 2),
    )
