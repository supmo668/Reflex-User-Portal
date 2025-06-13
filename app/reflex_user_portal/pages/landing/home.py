import reflex as rx
from ...backend.states.task.kit_subscribe import OnboardingTaskState

@rx.page(route="/", title="Home")
def home() -> rx.Component:
    return rx.vstack(
        rx.heading(
            "Home Page",
            size="5",
            align="center",
            width="100%",
        ),
        
        # Minimalist email subscription form
        rx.card(
            rx.vstack(
                rx.heading("Join Our Waitlist", size="4"),
                rx.text("Get early access to new features"),
                rx.hstack(
                    rx.input(
                        placeholder="Enter your email address",
                        value=OnboardingTaskState.email,
                        on_change=OnboardingTaskState.set_email,
                        flex="1",
                        type="email"
                    ),
                    rx.button(
                        "Subscribe",
                        on_click=OnboardingTaskState.subscribe_to_waitlist,
                        disabled=OnboardingTaskState.is_subscribing,
                        loading=OnboardingTaskState.is_subscribing,
                        color_scheme="blue"
                    ),
                    spacing="2",
                    width="100%"
                ),
                rx.cond(
                    OnboardingTaskState.subscription_status != "",
                    rx.text(
                        OnboardingTaskState.subscription_message,
                        color=rx.cond(
                            OnboardingTaskState.subscription_status == "success",
                            "green",
                            "red"
                        ),
                        font_weight="bold",
                        width="100%",
                    )
                ),
                spacing="3",
                width="100%"
            ),
            width="100%",
            max_width="400px"
        ),
        
        # Admin button
        rx.button(
            "Admin Profile",
            on_click=rx.redirect("/admin/profile"),
            variant="outline",
            margin_top="2em"
        ),
        
        spacing="4",
        width="100%",
        align_items="center",
        justify_content="center",
        padding="2em"
    )