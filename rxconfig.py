import reflex as rx
import reflex_user_portal.config as CONFIG

config = rx.Config(
    app_name="reflex_user_portal",
    db_url=CONFIG.DATABASE_URL,
)