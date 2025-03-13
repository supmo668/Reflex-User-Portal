"""User profile page."""

import reflex as rx
import reflex_clerk as clerk

from reflex_user_portal.templates import template
from reflex_user_portal.components.portal.profile import profile_content

@template(route="/profile", title="Profile")
def profile() -> rx.Component:
    """The protected profile page.

    Returns:
        The protected profile page component.
    """
    return profile_content()
