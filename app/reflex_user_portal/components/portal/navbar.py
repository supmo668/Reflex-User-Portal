"""Navbar component for the app."""

import reflex as rx
import reflex_clerk as clerk

from ... import styles
from .... import config
from ...views.logo import logo


def auth_components():
    return (
        rx.cond(
            clerk.ClerkState.is_signed_in,
            # Signed in
            rx.menu.root(
                rx.menu.trigger(
                    rx.button(
                        rx.hstack(
                            clerk.signed_in(
                                rx.cond(
                                    clerk.ClerkState.user.has_image,
                                    rx.avatar(
                                        src=clerk.ClerkState.user.image_url,
                                        name=clerk.ClerkState.user.first_name,
                                        size="3",
                                    ),
                                    rx.avatar(
                                        name=clerk.ClerkState.user.first_name,
                                        size="3",
                                    ),
                                ),
                            ),
                            rx.icon("chevron-down", size=16),
                            align="center",
                            height="100%",
                        ),
                        variant="ghost",
                        height="100%",
                    ),
                ),
                rx.menu.content(
                    rx.menu.item(
                        rx.hstack(
                            rx.text("Profile"),
                            rx.spacer(),
                            rx.icon("user", size=16),
                        ),
                        href="/admin/profile",
                    ),
                    rx.menu.separator(),
                    rx.menu.item(
                        clerk.signed_in(
                            rx.button(
                                clerk.sign_out_button(),
                                size="3",
                                color_scheme="gray",
                                background="black",
                            ),
                        ),
                    ),
                ),
                padding="1"
            ),
            # signed out
            clerk.signed_out(
                clerk.sign_in_button(
                    rx.button(
                        "Sign In",
                        size="3",
                        color_scheme="gray",
                        background="black",
                        height="40px",
                        padding="1",
                        # To ensure transparency, you can set background to "transparent" if needed
                        # background="transparent",
                    )
                ),
            ),
        )
    )

def navbar(with_clerk_wrapper: bool = False) -> rx.Component:
    """The navbar.

    Returns:
        The navbar component.
    """
    return rx.box(
        rx.hstack(
            # Left side - Brand/Logo
            logo(),
            # Center - App name
            rx.hstack(
                rx.link(
                    rx.heading(config.APP_DISPLAY_NAME, size="3", margin_y="1"),
                    href="/",
                    _hover={"text_decoration": "none"},
                    align="center",
                    height="100%",
                    padding_y="3",
                ),
                align="center",
            ),
            rx.spacer(),
            # Right side - Auth buttons
            auth_components(),
            width="100%",
            align="center",
        ),
        **styles.navbar_style,
    )
