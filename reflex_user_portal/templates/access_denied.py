import reflex as rx

def access_denied_page() -> rx.Component:
    """Access denied page."""
    return rx.vstack(
            rx.heading("Access Denied", size="3"),
            rx.text("You do not have permission to view this page."),
            justify="center",
            align="center",
            width="100%",
        )

def auth_redirect() -> rx.Component:
    """Auth redirect page that syncs user state and redirects to overview."""
    return rx.vstack(
        rx.heading("Redirecting...", size="3"),
        rx.spinner(),
        justify="center",
        align="center",
        height="100vh",
        width="100%",
    )