"""Authentication pages using Clerk."""

import reflex as rx

from reflex_user_portal.components.portal.sign_in import signin_page_content
from reflex_user_portal.templates import portal_template

@portal_template(route="/sign-in", title="Sign In")
def signin_page() -> rx.Component:
    return signin_page_content()
