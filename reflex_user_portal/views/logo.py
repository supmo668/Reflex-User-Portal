import reflex as rx

def logo():
    return rx.fragment(
        rx.box(
            rx.el.svg(
                rx.el.svg.path(
                    d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"
                ),
                rx.el.svg.path(d="M20 3v4"),
                rx.el.svg.path(d="M22 5h-4"),
                rx.el.svg.path(d="M4 17v2"),
                rx.el.svg.path(d="M5 18H3"),
                xmlns="http://www.w3.org/2000/svg",
                width="1.5rem",
                height="1.5rem",
                viewbox="0 0 24 24",
                fill="none",
                stroke="currentColor",
                stroke_width="2",
                stroke_linecap="round",
                stroke_linejoin="round",
                class_name="lucide lucide-sparkles",
                color="purple",
            ),
            href="/",
        )
    )
