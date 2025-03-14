"""Authentication pages using Clerk."""

import reflex as rx
import reflex_clerk as clerk
import os

from reflex_user_portal.templates import portal_template

def signin_page_content() -> rx.Component:
    return (
        rx.center(
            rx.vstack(
                clerk.sign_in(
                    path="/sign-in",
                ),
                align="center",
                spacing="7",
            ),
            height="100vh",
        )
    )

@portal_template(route="/sign-in", title="Sign In")
def signin_page() -> rx.Component:
    return signin_page_content()
