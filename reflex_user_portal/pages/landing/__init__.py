from .home import home
from .sign_in import signin_page

__all__ = ["home", "signin_page"]

def setup_pages(app):
    app.add_page(home, route="/", title="Home")
    app.add_page(signin_page, route="/sign-in", title="Sign In")
    app.add_page(signin_page, route="/sign-up", title="Sign Up")