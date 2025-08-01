# must import to initialize the application environment variables
from . import config as CONFIG

import reflex as rx
from fastapi import FastAPI

from .reflex_user_portal.pages import setup_pages

from .reflex_user_portal import styles
from .reflex_user_portal.utils.error_handler import custom_backend_handler

fastapi: FastAPI = FastAPI()

# Create app instance
app = rx.App(
    style=styles.base_style,
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;600;700;800;900&display=swap"
    ],
    # backend_exception_handler=custom_backend_handler,
    api_transformer=fastapi  # introduced in Reflex>0.7.0
)
# Add pages
setup_pages(app)

# prefer manually set-up for flexible page embedding (in setup_pages)
# clerk.install_pages(
#     app,
#     publishable_key=CONFIG.CLERK_PUBLISHABLE_KEY,
#     signin_route="/sign-in",
#     signup_route="/sign-up"
# )

# External API
from .reflex_user_portal.backend.api import setup_api
setup_api(app)