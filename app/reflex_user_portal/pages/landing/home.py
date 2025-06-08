import reflex as rx

@rx.page(route="/", title="Home")
def home() -> rx.Component:
    return rx.vstack(
        rx.heading(
            "Home Page",
            size="5",
            align="center",
            width="100%",
        ),
        rx.button(
            "Admin Profile",
            on_click=rx.redirect("/admin/profile"),
        ),
        spacing="2",  # Minimal space between heading and button
        width="100%",
        align_items="center",
        justify_content="center",
    )