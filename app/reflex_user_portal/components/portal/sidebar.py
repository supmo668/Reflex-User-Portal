"""Sidebar component for the app."""
import os
import reflex as rx

from ... import styles
from ...backend.states.admin.user import UserAuthState
from ...templates.template_config import NavItem, NAV_ITEMS

from ...views.logo import logo

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
        padding="2",
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
    active = UserAuthState.is_hydrated & (
        (rx.State.router.page.path == item.route.lower()) | (rx.State.router.page.path == "/overview") & (rx.State.router.page.path == "/")
    )

    return rx.cond(
        item.should_show(UserAuthState),
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


def sidebar_content():
    return rx.vstack(
        sidebar_header(),
        rx.vstack(
            *[sidebar_item(item) for item in NAV_ITEMS],
            spacing="1",
            width="100%",
            align_items="flex-start",
            padding_x="6",  # More space left/right
            padding_y="2",  # More space top/bottom
        ),
        rx.spacer(),
        sidebar_footer(),
        height="100%",
        justify_content="start",
        width="100%",
        padding_x="2",     # Outer padding for sidebar
        padding_y="2",
    )

def desktop_sidebar():
    return rx.tablet_and_desktop(
        rx.box(
            sidebar_content(),
            width="250px",
            height="100vh",
            bg=rx.color("gray", 2),
            position="fixed",
            top="64px",     # Offset by navbar height (e.g., 64px)
            left="0",
            min_width="0",
            z_index="1",
            padding_bottom="2",  # Bottom padding for comfort
        )
    )

def mobile_sidebar():
    return rx.mobile_only(
        rx.drawer.root(
            rx.drawer.trigger(
                rx.button("Menu", variant="outline", margin="1em"),
            ),
            rx.drawer.overlay(z_index="5"),
            rx.drawer.portal(
                rx.drawer.content(
                    sidebar_content(),
                    width="70vw",
                    height="100vh",
                    bg=rx.color("gray", 2),
                )
            ),
            direction="left",
        )
    )