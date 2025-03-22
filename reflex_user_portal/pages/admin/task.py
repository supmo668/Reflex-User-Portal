"""Welcome to Reflex! This file outlines the steps to create a basic app."""
import os

import reflex as rx
from reflex_user_portal.templates import portal_template

from reflex_user_portal.backend.states.task import MonitorState

API_URL = os.getenv("API_URL", "http://localhost:8000")
WS_URL = f"{API_URL}/ws"

@portal_template(route="/admin/tasks", title="Task Dashboard")
def task_status_display():
    """Display the status of tasks."""
    websocket_command = f"wscat -c {WS_URL}/tasks/{MonitorState.client_token}"
    api_command = f"curl {API_URL}/tasks/{MonitorState.client_token}"
    
    return rx.center(
        rx.vstack(
            rx.heading("Task Monitor"),
            rx.text("Client Token: ", MonitorState.client_token),
            rx.text("API Access:"),
            rx.hstack(
                rx.code_block(api_command, language="bash", can_copy=True),
            ),
            rx.text("WebSocket Connection:"),
            rx.code_block(websocket_command, language="bash", can_copy=True),
            rx.button(
                "Start New Task",
                on_click=MonitorState.long_running_task,
            ),
            rx.divider(),
            rx.heading("Active Tasks"),
            rx.foreach(
                MonitorState.current_active_tasks,
                lambda task: rx.vstack(
                    rx.heading(task.name, size="2"),
                    rx.text(f"Task ID: {task.id}"),
                    rx.text(f"Status: {task.status}"),
                    rx.progress(value=task.progress, max=100),
                    rx.text("Monitor this task:"),
                    rx.code_block(
                        f"{websocket_command}/{task.id}",
                        language="bash",
                        can_copy=True,
                    ),
                    padding="2",
                )
            ),
            rx.heading("Completed Tasks"),
            rx.foreach(
                MonitorState.completed_tasks,
                lambda task: rx.vstack(
                    rx.heading(task.name),
                    rx.text(f"Status: {task.status}"),
                    rx.text(f"Task ID: {task.id}"),
                    rx.text("Get task result:"),
                    rx.code_block(
                        f"{api_command}/{task.id}/result",
                        language="bash",
                        can_copy=True,
                    ),
                    padding="2",
                ),
            ),
            spacing="4",
        )
    )
