"""Admin pages package."""

from ...pages.admin.settings import admin_settings
from ...pages.admin.user_table import users_table
from ...pages.admin.task import task_status_display

__all__ = ["admin_settings", "users_table", "task_status_display"]

def setup_pages(app):
    """Setup admin pages."""
    # Register all admin pages
    app.add_page(admin_settings)
    app.add_page(users_table)
    app.add_page(task_status_display)
