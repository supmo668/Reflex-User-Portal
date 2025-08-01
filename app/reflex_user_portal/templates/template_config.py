"""Template configuration for the application."""

from dataclasses import dataclass
from typing import List, Type

import reflex as rx

from ..backend.states.admin.user import UserAuthState


@dataclass
class NavItem:
    """Navigation item configuration."""

    title: str
    route: str
    icon: str
    requires_auth: bool = False  # Whether this item requires authentication
    admin_only: bool = False  # Whether this item is only for admins

    def should_show(self, UserAuth: Type[UserAuthState]) -> rx.Var[bool]:
        """Check if this item should be shown based on auth state.

        Args:
            state: The user state class.

        Returns:
            A Var[bool] indicating if the item should be shown.
        """
        # For admin-required items, check admin status
        return rx.cond(
            UserAuth.is_hydrated,
            rx.cond(
                self.admin_only,
                UserAuth.is_admin,  # Admin check if needed
                True,  # Regular auth is enough
            ),
            False,
        )


# Define all navigation items in specified order
NAV_ITEMS = [
    NavItem(
        title="Overview",
        route="/admin/overview",
        icon="Home"
    ),
    NavItem(
        title="About",
        route="/admin/about",
        icon="book-open",
    ),
    NavItem(
        title="Profile",
        route="/admin/profile",
        icon="user",
        requires_auth=True,
    ),
    NavItem(
        title="App Settings",
        route="/admin/app-settings",
        icon="settings",
    ),
    NavItem(
        title="Admin Config",
        route="/admin/settings",
        icon="shield",
        requires_auth=True,
        admin_only=True,
    ),
    NavItem(
        title="User Table",
        route="/admin/users",
        icon="table-2",
        requires_auth=True,
        admin_only=True,
    ),
    NavItem(
        title="Task Monitor",
        route="/admin/tasks",
        icon="monitor",
        requires_auth=True,
        admin_only=True,
    ),
]
