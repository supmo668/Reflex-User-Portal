"""Common templates used between pages in the app."""

from typing import Callable, Optional, Union, List

import reflex as rx
import reflex_clerk as clerk

from .. import styles
from ..components.portal.navbar import navbar
from ..components.portal.sidebar import desktop_sidebar, mobile_sidebar  
from ..components.portal.profile import profile_content

from ..backend.states.admin.user import UserAuthState
from ..utils.logger import get_logger

from .access_denied import access_denied_page
from .template_config import NAV_ITEMS


logger = get_logger(__name__)

# Meta tags for the app.
default_meta = [
    {
        "name": "viewport",
        "content": "width=device-width, shrink-to-fit=no, initial-scale=1",
    },
]


def get_route_requirements(route: str) -> tuple[bool, bool]:
    """Get authentication requirements for a route.

    Args:
        route: The route to check.

    Returns:
        Tuple of (requires_auth, requires_admin).
    """
    for item in NAV_ITEMS:
        if route and route.startswith(item.route):
            return item.requires_auth, item.admin_only
    return False, False


class ThemeState(rx.State):
    """The state for the theme of the app."""

    accent_color: str = "crimson"
    gray_color: str = "gray"
    radius: str = "large"
    scaling: str = "100%"


def portal_template(
    route: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    meta: Optional[str] = None,
    script_tags: Optional[List[rx.Component]] = None,
    on_load: Optional[Union[rx.EventHandler, List[rx.EventHandler]]] = [
    ]
) -> Callable[[Callable[[], rx.Component]], rx.Component]:
    """The template for each page of the app.

    Args:
        route: The route to reach the page.
        title: The title of the page.
        description: The description of the page.
        meta: Additional meta tags to add to the page.
        script_tags: Additional script tags to add to the page.
        on_load: The event handler(s) called when the page loads.
    default:
        on_load: [UserAuthState.sync_auth_state] sync clerk state to internal user state

    Returns:
        The decorated page.
    """
    if isinstance(on_load, list):
        on_load = [UserAuthState.sync_auth_state, *on_load]
    elif isinstance(on_load, Union[rx.EventHandler, Callable]):
        on_load = [UserAuthState.sync_auth_state, on_load]
    # Get the meta tags for the page.
    all_meta = [*default_meta, *(meta or [])]
    # Get auth requirements from route
    requires_auth, requires_admin = get_route_requirements(route)
        
    def decorator(page_content: Callable[[], rx.Component]) -> rx.Component:
        """The template for each page of the app.

        Args:
            page_content: The content of the page.

        Returns:
            The template with the page content.
        """
        # Handle authentication requirements
        if requires_auth or requires_admin:
            # since these routes are hidden based on template_config.py, it shows access denied if directly accessed
            if requires_admin:
                content = rx.cond(
                    UserAuthState.is_hydrated,  # Not hydrated yet
                    rx.cond(
                        UserAuthState.is_admin,
                        page_content(),
                        access_denied_page()
                    ),
                    rx.spinner(),                # Or any loading component
                )
            else:
                content = rx.cond(
                    UserAuthState.is_hydrated,  # Not hydrated yet
                    rx.cond(
                        clerk.ClerkState.is_signed_in,
                        page_content(),
                        profile_content()
                    ),
                    rx.spinner(),                # Or any loading component
                )
        else:
            content = page_content()
        def templated_page():
            return rx.box(
                # Navbar (fixed)
                navbar(),
                # Main area: sidebar (fixed) + content (scrollable)
                rx.box(
                    desktop_sidebar(),
                    rx.scroll_area(
                        rx.vstack(
                            content,
                            **styles.template_content_style,
                        ),
                        **styles.template_scroll_area,
                    ),
                    **styles.template_main_area_style,  # <-- moved style here
                ),
                # Mobile sidebar (drawer)
                mobile_sidebar(),
                **styles.template_outer_box_style,  # <-- moved style here
            )

        @rx.page(
            route=route,
            title=title,
            description=description,
            meta=all_meta,
            script_tags=script_tags,
            on_load=on_load,
        )
        def theme_wrap():
            themed_page = rx.theme(
                clerk.clerk_provider(templated_page()),
                has_background=True,
                accent_color=ThemeState.accent_color,
                gray_color=ThemeState.gray_color,
                radius=ThemeState.radius,
                scaling=ThemeState.scaling,
            )
            return themed_page
        
        return theme_wrap

    return decorator
