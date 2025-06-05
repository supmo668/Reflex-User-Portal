import os

import reflex as rx
import app.config as CONFIG

from app.reflex_user_portal.utils.logger import get_logger
# Initialize logger
logger = get_logger(__name__)

# CORS origins
cors_origins = [CONFIG.FRONTEND_URL]  # Allow the public domain for CORS
if frontend_origin := os.getenv("RAILWAY_PUBLIC_DOMAIN"):
    cors_origins.append(frontend_origin)
logger.info(f"CORS origins: {cors_origins}")

# Configure Reflex app
config = rx.Config(
    app_name=os.getenv("REFLEX_APP_NAME", "app"),
    app_module_import="app.reflex_app",
    cors_allowed_origins=cors_origins,
    db_url=CONFIG.DATABASE_URL,
    api_url=CONFIG.API_URL,
    deploy_url=CONFIG.FRONTEND_URL,
    backend_host=os.getenv("BACKEND_HOST", "0.0.0.0"),
    show_built_with_reflex=False,
    tailwind=None,
)
print(f"Configuring Reflex with database URL: {CONFIG.DATABASE_URL.split('://')[0]}://<hidden>")  # Hide password in logs