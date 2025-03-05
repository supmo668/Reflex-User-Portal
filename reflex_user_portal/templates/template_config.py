"""Template configuration for the application."""

from dataclasses import dataclass
from typing import List, Type

import reflex as rx
import reflex_clerk as clerk

from reflex_user_portal.backend.user_state import UserState


@dataclass
class NavItem:
    """Navigation item configuration."""

    title: str
    route: str
    icon: str
    requires_auth: bool = False  # Whether this item requires authentication
    admin_only: bool = False  # Whether this item is only for admins

    def should_show(self, user_state: Type[UserState]) -> rx.Var[bool]:
        """Check if this item should be shown based on auth state.

        Args:
            state: The user state class.

        Returns:
            A Var[bool] indicating if the item should be shown.
        """
        # For admin-required items, check admin status
        return rx.cond(
                self.admin_only,
                user_state.is_admin,  # Admin check if needed
                True,  # Regular auth is enough
            )


# Define all navigation items in specified order
NAV_ITEMS = [
    NavItem(
        title="About",
        route="/about",
        icon="info",
    ),
    NavItem(
        title="Profile",
        route="/profile",
        icon="user",
        requires_auth=True,
    ),
    NavItem(
        title="App Settings",
        route="/settings",
        icon="settings",
    ),
    NavItem(
        title="Admin Config",
        route="/admin",
        icon="shield",
        requires_auth=True,
        admin_only=True,
    ),
    NavItem(
        title="User Table",
        route="/admin/users",
        icon="table",
        requires_auth=True,
        admin_only=True,
    ),
]
