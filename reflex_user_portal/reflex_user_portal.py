import reflex_user_portal.config as CONFIG
import reflex as rx
import reflex_clerk as clerk

from reflex_user_portal.pages.landing import setup_pages as setup_landing_pages
from reflex_user_portal.pages.portal import setup_pages as setup_portal_pages
from reflex_user_portal.pages.admin import setup_pages as setup_admin_pages

import reflex_user_portal.styles as styles


# Create app instance
app = rx.App(
    style=styles.base_style,
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;600;700;800;900&display=swap",
    ]
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
from reflex_user_portal.backend.api import setup_task_apis
setup_task_apis(app)