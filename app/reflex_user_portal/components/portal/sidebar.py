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
    """Sidebar footer."""
    return rx.box(
        rx.vstack(
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
                padding="0",
            ),
            width="100%",
            spacing="0",
        ),
        **styles.sidebar_footer_style,
    )

def sidebar_item(item: NavItem) -> rx.Component:
    """Create a sidebar item.

    Args:
        item: The navigation item configuration.

    Returns:
        The sidebar item component.
    """
    # Whether the item is active: currently selected or default page
    current_tab = rx.cond(
        # check whether the current tab is the item route or the default route
        (rx.State.router.page.path == item.route.lower()) | (rx.State.router.page.path == "/overview") & (rx.State.router.page.path == "/"),
        True, False
    )

    return rx.cond(
        UserAuthState.is_hydrated,
        rx.cond(
            item.should_show(UserAuthState),
            # have access to this item
            rx.link(
                rx.hstack(
                    rx.icon(item.icon, size=18),
                    rx.text(item.title, size="3"),
                    width="100%",
                    color=rx.cond(
                        current_tab,
                        styles.accent_text_color,
                        styles.text_color,
                    ),
                    bg=rx.cond(
                        current_tab,
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
                                current_tab,
                                styles.accent_bg_color,
                                styles.gray_bg_color,
                            ),
                            "color": rx.cond(
                                current_tab,
                                styles.accent_text_color,
                                styles.text_color,
                            ),
                        }
                    },
                ),
                href=item.route,
                width="100%",
            ),
            # No access to this item
            rx.box(),
        ),
        rx.box(),
    )

def sidebar_content():
    return rx.box(
        rx.vstack(
            sidebar_header(),
            rx.vstack(
                *[sidebar_item(item) for item in NAV_ITEMS],
                spacing="1",
                width="100%",
                align_items="flex-start",
            ),
            rx.spacer(),
            width="100%",
        ),
        **styles.sidebar_content_style,
    )

def desktop_sidebar():
    return rx.tablet_and_desktop(
        rx.box(
            rx.vstack(
                sidebar_content(),
                sidebar_footer(),
                width="100%",
                height="100%",
                spacing="0",
            ),
            **styles.sidebar_style,
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
                    rx.vstack(
                        sidebar_content(),
                        sidebar_footer(),
                        width="100%",
                        height="100%",
                        spacing="0",
                    ),
                    width="70vw",
                    height="100vh",
                    bg=rx.color("gray", 2),
                )
            ),
            direction="left",
        )
    )