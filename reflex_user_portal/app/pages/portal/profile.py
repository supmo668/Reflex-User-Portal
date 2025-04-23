"""User profile page."""

import reflex as rx

from ...templates import portal_template
from ...backend.states.admin.user import UserAttributeState
from ...components.portal.profile import profile_content

@portal_template(route="/profile", title="Profile")
def profile() -> rx.Component:
    """The protected profile page.

    Returns:
        The protected profile page component.
    """
    return profile_content()

def collection_view():
    return rx.vstack(
        rx.button(
            "Add to Favorites",
            on_click=lambda: UserAttributeState.add_to_collection(
                "favorites", 
                {"id": 1, "name": "Item 1"}
            )
        ),
        rx.foreach(
            UserAttributeState.user_collections.get("favorites", []),
            lambda item: rx.text(item["name"])
        )
    )