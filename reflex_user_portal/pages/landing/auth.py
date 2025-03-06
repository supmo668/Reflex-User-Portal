"""Authentication redirection page."""
import reflex as rx

from reflex_user_portal.backend.user_state import UserState
from reflex_user_portal.templates.template import template


@template(route="/auth/redirect", title="Redirecting...", on_load=[
            UserState.sync_auth_state,
            UserState.auth_redirect,
        ])
def auth_redirect() -> rx.Component:
    """Auth redirect page that syncs user state and redirects to overview."""
    return rx.vstack(
        rx.heading("Redirecting...", size="3"),
        rx.spinner(),
        justify="center",
        align="center",
        height="100vh",
    )