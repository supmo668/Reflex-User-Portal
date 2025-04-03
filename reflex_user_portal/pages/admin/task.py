from typing import Type
import reflex as rx


from reflex_user_portal.templates import portal_template
from reflex_user_portal.backend.states.task import DisplayMonitorState, STATE_MAPPINGS
from reflex_user_portal.backend.api.commands import format_command

def wrapped_code_block(text: str, language: str = None, can_copy: bool = True) -> rx.Component:
    """Helper function to create a consistently styled code block."""
    return rx.box(
        rx.code_block(
            text,
            language=language,
            can_copy=can_copy,
            width="100%",
            overflow_x="auto",
        ),
        width="100%",
    )

def task_info_section(label: str, content: str, language: str = None) -> rx.Component:
    """Helper function to create a labeled code block section."""
    return rx.vstack(
        rx.text(label),
        wrapped_code_block(content, language),
        width="100%",
    )

def task_command_section(label: str, command: str) -> rx.Component:
    """Helper function to create a command section."""
    return task_info_section(label, command, language="bash")

DEFAULT_STATE_NAME = "ExampleTaskState"

@portal_template(route="/admin/tasks", title="Task Dashboard")
def task_status_display():
    """Display the status of tasks."""
    DefaultTaskState: Type[rx.State] = STATE_MAPPINGS[DEFAULT_STATE_NAME].get("cls")
    def get_command(cmd_type: str, state_name: str=DEFAULT_STATE_NAME, **kwargs) -> str:
        state_info = STATE_MAPPINGS[state_name]
        return format_command(
            cmd_type,
            state_info,
            client_token=DefaultTaskState.client_token,
            **kwargs
        )
    
    return rx.container(
        rx.vstack(
            rx.heading("Task Monitor"),
            rx.flex(
                rx.text("State Type:"),
                rx.select.root(
                    rx.select.trigger(),
                    rx.select.content(
                        rx.foreach(
                            DisplayMonitorState.state_mappings,
                            lambda item: rx.select.item(item[0], value=item[0])
                        )
                    ),
                    value=DisplayMonitorState.current_state_type,
                    on_change=DisplayMonitorState.change_state_type,
                ),
                rx.text("Task: "),
                rx.select.root(
                    rx.select.trigger(),
                    rx.select.content(
                        rx.foreach(
                            DisplayMonitorState.task_functions,
                            lambda item: rx.select.item(
                                f"{item[0]}: {item[1]}", value=item[0])
                        )
                    ),
                    value=DisplayMonitorState.current_task_function,
                    on_change=DisplayMonitorState.change_task_function,
                ),
                wrap="wrap",
                spacing="2",
            ),
            task_info_section("Client Token (All Tasks):", DefaultTaskState.client_token),
            task_info_section("Session ID (All Tasks):", DefaultTaskState.session_id),
            task_info_section("Base API Path:", DisplayMonitorState.base_api_path, "bash"),
            
            # API Commands Section
            rx.box(
                rx.vstack(
                    rx.heading("API Commands", size="4"),
                    task_command_section("Get All Tasks Status:", DisplayMonitorState.status_command),
                    task_command_section("Get Single Task Status:", DisplayMonitorState.task_status_command),
                    task_command_section("Start Selected Task:", DisplayMonitorState.start_command),
                    task_command_section("additional parameters:", DisplayMonitorState.formatted_curl_body),
                    task_command_section("Get Task Result:", DisplayMonitorState.result_command),
                    
                    rx.heading("WebSocket Commands", size="4"),
                    task_command_section("Monitor All Tasks:", DisplayMonitorState.ws_status_command),
                    task_command_section("Monitor Specific Task:", DisplayMonitorState.ws_task_command),
                    padding="4",
                    border="1px solid",
                    border_radius="md",
                    width="100%",
                ),
                padding="4",
                border="1px solid",
                width="100%",
            ),
            rx.button(
                "Start Selected Task",
                on_click=DefaultTaskState.task1,
            ),
            rx.divider(),
            
            # Active Tasks Section
            rx.heading("Active Tasks (Example Task Only)"),
            rx.foreach(
                DefaultTaskState.active_tasks,
                lambda task: rx.vstack(
                    rx.heading(task.name, size="2"),
                    rx.text(f"Task ID: {task.id}"),
                    rx.text(f"Status: {task.status}"),
                    rx.progress(value=task.progress, max=100),
                    task_command_section(
                        "Monitor this task:",
                        get_command("ws_task", DEFAULT_STATE_NAME, task_id=task.id)
                    ),
                    padding="2",
                    width="100%",
                )
            ),
            
            # Completed Tasks Section
            rx.heading("Completed Tasks (Example Task Only)"),
            rx.foreach(
                DefaultTaskState.completed_tasks,
                lambda task: rx.vstack(
                    rx.heading(task.name),
                    rx.text(f"Status: {task.status}"),
                    rx.text(f"Task ID: {task.id}"),
                    task_command_section(
                        "Get task result:",
                        get_command("result", DEFAULT_STATE_NAME, task_id=task.id)
                    ),
                    padding="2",
                    width="100%",
                ),
            ),
            spacing="4",
            width="100%",
        ),
        size="3",
    )