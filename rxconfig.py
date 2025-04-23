import reflex as rx
import reflex_user_portal.config as CONFIG

config = rx.Config(
    app_name="app",
    app_module_import="reflex_user_portal.reflex_app",
    show_built_with_reflex=False,
    db_url=CONFIG.DATABASE_URL,
)
print(f"Configuring Reflex with database URL: {CONFIG.DATABASE_URL.split("://")[0]}://<hidden>")  # Hide password in logs