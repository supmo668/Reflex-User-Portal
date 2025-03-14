import reflex as rx

rx.page(route="/home", title="Home")
def home() -> rx.Component:
    return rx.fragment(
        rx.box(
            rx.heading("Home Page", size="5", justify="center", align="center", width="100%"),
            font_family='system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji"',
            min_height="100vh",
        )
    )
