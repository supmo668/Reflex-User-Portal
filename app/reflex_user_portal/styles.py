"""Styles for the app."""

import reflex as rx
from reflex_clerk.lib.appearance import Appearance, AppearanceVariables

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
    "width": "100%",
    "align_items": "center",
    "justify_content": "center",
    "overflow_y": "auto",
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
    "height": f"calc(100vh - {NAVBAR_HEIGHT})",  # Leave space for navbar
    "margin_top": NAVBAR_HEIGHT,            # Offset content below navbar
    "overflow_y": "auto",
}

# Add the moved styles here
template_main_area_style = {
    "width": "100vw",
    "display": "flex",
    "align_items": "stretch",
    "position": "relative",
    "height": "100vh",        
    # REMOVE margin_top and subtraction of NAVBAR_HEIGHT
    # "padding_top": NAVBAR_HEIGHT,
}

template_outer_box_style = {
    "height": "100vh",
    "width": "100vw",
    "overflow": "auto",
    # "padding_top": NAVBAR_HEIGHT,
}

navbar_style = {
    "bg": gray_bg_color,
    "border_bottom": f"1px solid {border_color}",
    # REMOVE or COMMENT OUT the following line:
    "position": "fixed",
    "top": "0",
    "left": "0",
    "width": "100vw",
    "height": NAVBAR_HEIGHT,
    "padding_x": "1.5em",  # Increase horizontal padding
    "padding_y": "0.75em", # Add some vertical padding
    "margin": "1",
    "display": "flex",
    "align_items": "center",
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

base_stylesheets = [
    "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap"
]
