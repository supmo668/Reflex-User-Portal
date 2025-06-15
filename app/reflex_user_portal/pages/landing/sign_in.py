"""Authentication pages using Clerk."""

import reflex as rx
import reflex_clerk as clerk 

from ...templates import portal_template


@portal_template(route="/sign-in", title="Sign In")
def signin_page() -> rx.Component:
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
