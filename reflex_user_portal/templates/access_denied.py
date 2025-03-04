import reflex as rx

def access_denied_page() -> rx.Component:
    """Access denied page."""
    return rx.vstack(
            rx.heading("Access Denied", size="3"),
            rx.text("You do not have permission to view this page."),
            width="100%",
        )