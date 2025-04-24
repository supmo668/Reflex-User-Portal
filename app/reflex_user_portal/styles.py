"""Styles for the app."""

import reflex as rx
from reflex_clerk.lib.appearance import Appearance, AppearanceVariables

# Colors
border_radius = "var(--radius-2)"
border = f"1px solid {rx.color('gray', 5)}"
text_color = rx.color("gray", 11)
gray_color = rx.color("gray", 11)
gray_bg_color = rx.color("gray", 3)
accent_text_color = rx.color("accent", 10)
accent_color = rx.color("accent", 1)
accent_bg_color = rx.color("accent", 3)
hover_accent_color = {"_hover": {"color": accent_text_color}}
hover_accent_bg = {"_hover": {"background_color": accent_color}}

# Layout
content_width_vw = "90vw"
sidebar_width = "20rem"
sidebar_content_width = "16rem"
max_width = "1480px"
color_box_size = ["2.25rem", "2.25rem", "2.5rem"]

# Theme colors
bg_color = gray_bg_color
border_color = rx.color("gray", 4)
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

# Template styles
template_page_style = {
    "padding_x": ["auto", "auto", "2em"],
    "grow":"1",
    "min_width": "0",
    "height": "100vh",
    "overflow_y": "auto",
    "margin_left": ["0", "0", "250px"],
    "padding_top": ["4em", "4em", "5em"],
}

template_content_style = {
    "padding": "1em",
    "margin_bottom": "2em",
    "min_height": "90vh",
    "width": "100%",
    "align_items": "center",
    "justify_content": "center",
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
