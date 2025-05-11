"""Portal pages package."""

from .settings import app_settings
from .about import about
from .profile import profile
from .overview import overview

__all__ = ["app_settings", "about", "profile", "overview"]

def setup_pages(app):
    """Setup portal pages."""
    # Register all portal pages
    app.add_page(overview)
    # app.add_page(profile)
    # app.add_page(about)
    # app.add_page(app_settings)
    