"""User profile page."""

import reflex as rx
import reflex_clerk as clerk

from ...templates import template


def profile_content() -> rx.Component:
    """Profile page content showing user information.

    Returns:
        The profile page content.
    """
    return rx.vstack(
        rx.heading("Profile", size="5"),
        rx.vstack(
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
            rx.vstack(
                rx.text("Name", weight="bold"),
                rx.cond(
                    (clerk.ClerkState.user.first_name != "") & (clerk.ClerkState.user.last_name != ""),
                    rx.text(clerk.ClerkState.user.first_name + " " + clerk.ClerkState.user.last_name),
                    rx.text("Not provided"),
                ),
                border="1px solid var(--gray-200)",
                border_radius="md",
                padding="4",
            ),
            rx.vstack(
                rx.text("Email", weight="bold"),
                rx.foreach(
                    clerk.ClerkState.user.email_addresses,
                    lambda email: rx.text(email.email_address),
                ),
                border="1px solid var(--gray-200)",
                border_radius="md",
                padding="4",
            ),
            width="100%",
            max_width="400px",
            spacing="4",
            align_items="center",
        ),
        spacing="8",
        width="100%",
    )


@template(route="/profile", title="Profile")
def profile() -> rx.Component:
    """The protected profile page.

    Returns:
        The protected profile page component.
    """
    return profile_content()
