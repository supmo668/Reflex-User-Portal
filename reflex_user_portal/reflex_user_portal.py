import reflex_user_portal.config as CONFIG
import reflex as rx
import reflex_clerk as clerk

from reflex_user_portal.pages.landing import landing, signin_page, auth_redirect
from reflex_user_portal.pages.admin import admin_settings, users_table
from reflex_user_portal.pages.portal import about, profile, app_settings, index
import reflex_user_portal.styles as styles

# Create app instance
app = rx.App(
    style=styles.base_style,
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;600;700;800;900&display=swap",
    ]
)

# Add pages
app.add_page(landing, route="/", title="Home")

# Portal pages
app.add_page(index, route="/overview", title="Overview")  
app.add_page(users_table, route="/admin/users", title="User Management")  
app.add_page(profile)
app.add_page(admin_settings)
app.add_page(about)
app.add_page(app_settings)

# sign-ins
app.add_page(signin_page, route="/sign-in")
app.add_page(signin_page, route="/sign-up")
app.add_page(auth_redirect, route="/auth/redirect")

clerk.install_pages(
    app,
    publishable_key=CONFIG.CLERK_PUBLISHABLE_KEY,
    force_redirect_url="/auth/redirect",
    signin_route="/sign-in",
    signup_route="/sign-up"
)