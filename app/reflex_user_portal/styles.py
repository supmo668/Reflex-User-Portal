"""Styles for the app."""

import reflex as rx
from reflex_clerk_api.user_components import Appearance
from reflex_clerk_api.models import Variables as AppearanceVariables

# Colors
border_radius = "var(--radius-2)"
border_color = rx.color("gray", 4)  # <-- define before use
border = f"1px solid {rx.color('gray', 5)}"
text_color = rx.color("gray", 11)
gray_color = rx.color("gray", 11)
gray_bg_color = rx.color("gray", 3)
accent_text_color = rx.color("accent", 10)
accent_color = rx.color("accent", 1)
accent_bg_color = rx.color("accent", 3)
hover_accent_color = {"_hover": {"color": accent_text_color}}
hover_accent_bg = {"_hover": {"background_color": accent_color}}

# --- Layout & Sidebar Styles ---

SIDEBAR_WIDTH = "250px"
NAVBAR_HEIGHT = "56px"
color_box_size = ["2.25rem", "2.25rem", "2.5rem"]

sidebar_style = {
    "width": SIDEBAR_WIDTH,
    "height": f"calc(100vh - {NAVBAR_HEIGHT})",
    "position": "fixed",
    "top": NAVBAR_HEIGHT,
    "left": "0",
    "bg": gray_bg_color,
    "z_index": "1",
    "display": "flex",
    "flex_direction": "column",
    "padding": "0",
    "border_right": f"1px solid {border_color}",
    "flex_shrink": "0",
}

sidebar_content_style = {
    "flex": "1 1 auto",
    "overflow_y": "auto",
    "width": "100%",
    "padding_x": "1.5em",
    "padding_y": "1em",
}

sidebar_footer_style = {
    "width": "100%",
    "padding": "1em",
    "border_top": f"1px solid {border_color}",
    "bg": gray_bg_color,
}

template_content_style = {
    "padding": "2em 1.5em 2em 1.5em",
    "margin": "0",
    "min_height": "100%",
    # Remove or adjust width to allow centering
    # "width": "100%",  # Comment this out or set to "auto"
    "align_items": "center",
    "justify_content": "center",
    "overflow_y": "auto",
    "display": "flex",           # Ensure flex layout
    "flex_direction": "column",  # Stack children vertically
}

template_container_style = {
    "margin_left": [ "0", "0", SIDEBAR_WIDTH ],
    "padding": "0",
    "min_width": "0",
    "height": "100%",        # REMOVE subtraction of NAVBAR_HEIGHT
    "overflow": "auto",
    "grow": "1",
    "padding_top": "0",
    "width": "100%",
    "align_items": "center",            # Center children inside vstack
    "justify_content": "center",
    "display": "flex"
}

template_scroll_area = {
    "height": f"calc(100vh - {NAVBAR_HEIGHT})",
    "margin_top": NAVBAR_HEIGHT,
    "margin_left": SIDEBAR_WIDTH,      # <-- Add this line
    "overflow_y": "auto",
    "flex_grow": "1",
    "min_width": "0"
}

# Add the moved styles here
template_main_area_style = {
    "width": "100%",
    "height": "100vh",
    "display": "flex",
    "align_items": "stretch",
    "position": "relative",
    "flex_grow": "1"
    # REMOVE margin_top and subtraction of NAVBAR_HEIGHT
    # "padding_top": NAVBAR_HEIGHT,
}

template_outer_box_style = {
    "height": "100%",
    "width": "100%",
    # "overflow_x": "hidden",  # Prevent horizontal scroll
    # "padding_top": NAVBAR_HEIGHT,
}

navbar_style = {
    "bg": gray_bg_color,
    "border_bottom": f"1px solid {border_color}",
    "position": "fixed",
    "top": "0",
    "left": "0",
    "width": "100%",
    "height": NAVBAR_HEIGHT,
    "padding_x": "1.5em",
    "padding_y": "0.75em",
    "margin": "1",
    "display": "flex",
    "align_items": "center",
    "z_index": 1000,
}

# Theme colors
bg_color = gray_bg_color
danger_color = rx.color("red", 9)

# Clerk sign-in appearance

# Create appearance config using Clerk's models
ORANGE = {
    "50": "#FFF5EE",
    "100": "#FFE5B4", 
    "500": "#FF6347",  # Main orange
    "600": "#FF4500",
    "700": "#FF3300",
}

# Define the Clerk styles using the Appearance class
CLERK_STYLES = Appearance(
    baseTheme="default",  # Can be "default", "dark", "shadesOfPurple", "neobrutalism"
    variables=AppearanceVariables(
        colorPrimary=ORANGE["500"]
    ),
    elements={
        "formButtonPrimary": {
            "backgroundColor": ORANGE["500"],
            "color": "white",
            "hover": {
                "backgroundColor": ORANGE["600"]
            }
        },
        "card": {
            "borderColor": ORANGE["100"],
            "backgroundColor": ORANGE["50"]
        },
        "headerTitle": {
            "color": ORANGE["500"]
        }
    }
)

# Base style for the app
base_style = {
    "font_family": "Inter",
    "background": bg_color,
    rx.button: {
        "_hover": {
            "transform": "scale(1.02)",
            "transition": "transform 0.2s ease-in-out",
        }
    },
    rx.link: {
        "text_decoration": "none",
        "_hover": {"text_decoration": "none"},
    },
}

link_style = {
    "color": accent_text_color,
    "text_decoration": "none",
    **hover_accent_color,
}

overlapping_button_style = {
    "background_color": "white",
    "border_radius": border_radius,
}

markdown_style = {
    "code": lambda text: rx.code(text, color_scheme="gray"),
    "codeblock": lambda text, **props: rx.code_block(text, **props, margin_y="1em"),
    "a": lambda text, **props: rx.link(
        text,
        **props,
        font_weight="bold",
        text_decoration="underline",
        color=accent_text_color,
        _hover={"color": accent_color},
    ),
}

notification_badge_style = {
    "width": "1.25rem",
    "height": "1.25rem",
    "display": "flex",
    "align_items": "center",
    "justify_content": "center",
    "position": "absolute",
    "right": "-0.35rem",
    "top": "-0.35rem",
}

ghost_input_style = {
    "--text-field-selection-color": "",
    "--text-field-focus-color": "transparent",
    "--text-field-border-width": "1px",
    "background_clip": "content-box",
    "background_color": "transparent",
    "box_shadow": "inset 0 0 0 var(--text-field-border-width) transparent",
    "color": "",
}

box_shadow_style = "0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)"

color_picker_style = {
    "border_radius": "max(var(--radius-3), var(--radius-full))",
    "box_shadow": box_shadow_style,
    "cursor": "pointer",
    "display": "flex",
    "align_items": "center",
    "justify_content": "center",
    "transition": "transform 0.15s ease-in-out",
    "_active": {
        "transform": "translateY(2px) scale(0.95)",
    },
}

professional_toast_style = {
    "background_color": "#fff",
    "color": "#222",
    "border": "1px solid #E0E0E0",
    "border_radius": "8px",
    "box_shadow": "0 4px 24px 0 rgba(0,0,0,0.06)",
    "padding": "1.25em 2em",
    "font_size": "1.05em",
    "font_weight": "500",
    "min_width": "320px",
    "max_width": "420px",
}

professional_toast_args = {
    "duration": 5000,
    "position": "top-right",
    "close_button": True,
    "invert": False,
    "important": True,
    "style": professional_toast_style,
}

# Example usage:
# rx.button(
#     "Show Toast",
#     on_click=rx.toast(**professional_toast_args),
# )

base_stylesheets = [
    "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap"
]
