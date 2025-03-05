"""Navbar component for the app."""

import reflex as rx
import reflex_clerk as clerk

import reflex_user_portal.styles as styles
import reflex_user_portal.config as config


def auth_components():
    return (
        clerk.clerk_loaded(
            rx.cond(
                clerk.ClerkState.is_signed_in,
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
                                            size="5",
                                        ),
                                        rx.avatar(
                                            name=clerk.ClerkState.user.first_name,
                                            size="5",
                                        ),
                                    ),
                                ),
                                rx.icon("chevron-down", size=14),
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
                            href="/profile",
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
                ),
                clerk.signed_out(
                    rx.button(
                        clerk.sign_in_button(),
                        size="3",
                        color_scheme="gray",
                        background="black",
                        height="40px",  # Fixed height for sign in button
                    ),
                ),
            ),
        ),
    )

def navbar(with_clerk_wrapper: bool = False) -> rx.Component:
    """The navbar.

    Returns:
        The navbar component.
    """
    return rx.box(
        rx.hstack(
            # Left side - Brand/Logo
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
            clerk.clerk_provider(auth_components()) if with_clerk_wrapper else auth_components(),
            width="100%",
            padding_x="4",
            height="100%",
            max_width=styles.max_width,
            margin="0 auto",
            align="center",
        ),
        bg=styles.gray_bg_color,
        border_bottom=f"1px solid {styles.border_color}",
        position="sticky",
        top="0",
        z_index="100",
        height="64px",
        width="100%",
    )
