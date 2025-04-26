import reflex as rx

from ...backend.states.admin.admin_api_panel_state import BaseState

navbar: dict[str, str] = {
    "width": "100%",
    "padding": "1em 1.15em",
    "justify_content": "space-between",
    "bg": rx.color_mode_cond(
        "rgba(255, 255, 255, 0.81)",
        "rgba(18, 17, 19, 0.81)",
    ),
    "align_items": "center",
    "border_bottom": "1px solid rgba(46, 46, 46, 0.51)",
}


def render_navbar():
    return rx.hstack(
        rx.hstack(
            rx.box(
                rx.text(
                    "REST API Admin Panel",
                    # font_size="var(--chakra-fontSizes-lg)",
                ),
            ),
            display="flex",
            align_items="center",
        ),
        rx.hstack(
            rx.button(
                BaseState.is_request, 
                on_click=BaseState.toggle_query, cursor="pointer"
            ),
            rx.color_mode.button(),
            align_items="center",
        ),
    )
