import reflex_user_portal.config as config
import reflex as rx
import reflex_clerk as clerk

from reflex_user_portal.pages.landing import landing, sign_in
from reflex_user_portal.pages.admin import admin_settings, table
from reflex_user_portal.pages.portal import about, profile, app_settings
import reflex_user_portal.styles as styles

# Create app instance
app = rx.App(
    style=styles.base_style,
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;600;700;800;900&display=swap",
    ],
)

# Add pages
app.add_page(landing)
app.add_page(table, route="/admin/users", title="User Management")  
app.add_page(profile)
app.add_page(admin_settings)
app.add_page(about)
app.add_page(app_settings)

clerk.install_signin_page(app, route="/sign-in")