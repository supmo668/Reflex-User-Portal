import reflex as rx
import reflex_clerk as clerk

from . import config as CONFIG

from .reflex_user_portal.pages.landing import setup_pages as setup_landing_pages
from .reflex_user_portal.pages.portal import setup_pages as setup_portal_pages
from .reflex_user_portal.pages.admin import setup_pages as setup_admin_pages

from .reflex_user_portal import styles
from .reflex_user_portal.utils.error_handler import custom_backend_handler

# Create app instance
app = rx.App(
    style=styles.base_style,
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;600;700;800;900&display=swap"
    ],
    backend_exception_handler=custom_backend_handler,
)

# Add pages
setup_landing_pages(app)
# Portal pages
setup_portal_pages(app)
# Admin pages
setup_admin_pages(app)

clerk.install_pages(
    app,
    publishable_key=CONFIG.CLERK_PUBLISHABLE_KEY,
    signin_route="/sign-in",
    signup_route="/sign-up"
)

# External API
from .reflex_user_portal.backend.api import setup_api
setup_api(app)