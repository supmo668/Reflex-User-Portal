import reflex as rx
import reflex_clerk as clerk

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