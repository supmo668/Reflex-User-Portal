import reflex as rx
from .home import home
from .sign_in import signin_page

from ...templates import portal_template

__all__ = ["home", "signin_page"]

def setup_pages(app: rx.App=None):
    app.add_page(home, route="/", title="Home")
    @portal_template(route="/sign-in", title="Sign In")
    def signin_page_template():
        return signin_page()
    pass