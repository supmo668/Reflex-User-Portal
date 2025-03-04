"""Admin pages package."""

from reflex_user_portal.pages.admin.settings import admin_settings
from reflex_user_portal.pages.admin.user_table import users_table

__all__ = ["admin_settings", "users_table"]
