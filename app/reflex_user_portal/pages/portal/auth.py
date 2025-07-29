"""Authentication pages using Clerk."""

import reflex as rx
import reflex_clerk_api as clerk


def signin() -> rx.Component:
    """Sign in page with Clerk's sign-in component.

    Returns:
        The sign in page component.
    """
    return clerk.clerk_provider(
        rx.center(
            rx.vstack(
                clerk.sign_in(
                    path="/signin",
                ),
                align="center",
                spacing="7",
            ),
            height="100vh",
        ),
    )


def signup() -> rx.Component:
    """Sign up page with Clerk's sign-up component.

    Returns:
        The sign up page component.
    """
    return clerk.clerk_provider(
        rx.center(
            rx.vstack(
                clerk.sign_up(
                    path="/signup",
                ),
                align="center",
                spacing="7",
            ),
            height="100vh",
        ),
    )