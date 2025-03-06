"""Authentication pages using Clerk."""

import reflex as rx
import reflex_clerk as clerk
import os

def signin_page() -> rx.Component:
    return clerk.clerk_provider(
        rx.center(
            rx.vstack(
                clerk.sign_in(
                    path="/sign-in",
                ),
                align="center",
                spacing="7",
            ),
            height="100vh",
        ),
    )


def signin_component() -> rx.Component:
    return rx.hstack(
        rx.flex(
            clerk.user_button(),
            width="100%",
            spacing="7",
            margin_top="0.75rem",
            padding_right="0.75rem",
            direction="column",
            align="end",

        ),
        rx.center(
            rx.vstack(
                clerk.signed_in(
                    rx.cond(
                        clerk.ClerkState.user.has_image,
                        rx.avatar(
                            src=clerk.ClerkState.user.image_url,
                            name=clerk.ClerkState.user.first_name,
                            size="4",
                        ),
                    )
                ),
                rx.heading(f"Welcome to {os.getenv('APP_DISPLAY_NAME')}!", size="9"),
                clerk.signed_out(
                    rx.button(
                        clerk.sign_in_button(),
                        size="3",
                        color_scheme="gray",
                        background="black"
                    ),
                ),
                clerk.signed_in(
                    rx.button(
                        clerk.sign_out_button(),
                        size="3",
                        color_scheme="gray",
                        background="black"
                    )
                ),
                clerk.clerk_loaded(
                    rx.cond(
                        clerk.ClerkState.is_signed_in,
                        rx.box(
                            rx.text(
                                "You are currently logged in as ",
                                clerk.ClerkState.user.first_name
                            ),
                        ),
                        rx.text("you are currently logged out"))),

                align="center",
                spacing="7",
            ),
            height="100vh",

        ),
    )

def to_signin_page(with_clerk_wrapper: bool = False) -> rx.Component:
    return clerk.clerk_provider(signin_component()) if with_clerk_wrapper else signin_component()
