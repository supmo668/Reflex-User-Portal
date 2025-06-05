import os

import reflex as rx
import app.config as CONFIG

# CORS origins
cors_origins = [CONFIG.FRONTEND_URL]  # Allow the public domain for CORS
if frontend_origin := os.getenv("RAILWAY_PUBLIC_DOMAIN"):
    cors_origins.append(frontend_origin)

config = rx.Config(
    app_name=os.getenv("REFLEX_APP_NAME", "app"),
    app_module_import="app.reflex_app",
    show_built_with_reflex=False,
    tailwind=None,
    db_url=CONFIG.DATABASE_URL,
    api_url=CONFIG.API_URL,
    deploy_url=CONFIG.FRONTEND_URL,
    backend_host=os.getenv("BACKEND_HOST", "0.0.0.0"),
)
print(f"Configuring Reflex with database URL: {CONFIG.DATABASE_URL.split('://')[0]}://<hidden>")  # Hide password in logs