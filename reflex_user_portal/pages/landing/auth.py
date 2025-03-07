"""Authentication redirection page."""
import reflex as rx
import reflex_clerk as clerk

from reflex_user_portal.backend.user_state import UserState, UserType
from reflex_user_portal.config import ADMIN_USER_EMAILS
from reflex_user_portal.models.user import User
from reflex_user_portal.templates.template import template


@template(route="/auth/redirect", title="Redirecting...", on_load=[
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