from typing import Type
import reflex as rx


from ...templates import portal_template
from ...backend.states.task import DisplayMonitorState, STATE_MAPPINGS
from ...backend.api.commands import format_command

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
        padding_x="2",
        width="100%",
    )

def task_info_section(label: str, content: str, language: str = None) -> rx.Component:
    """Helper function to create a labeled code block section."""
    return rx.vstack(
        rx.text(label),
        wrapped_code_block(content, language),
        width="100%",
    )

DEFAULT_STATE_NAME = "ExampleTaskState"

@portal_template(route="/admin/tasks", title="Task Dashboard", on_load=DisplayMonitorState.preselect_task_function)
def task_status_display():
    """Display the status of tasks."""
    DefaultTaskState: Type[DisplayMonitorState] = STATE_MAPPINGS[DEFAULT_STATE_NAME].get("cls")
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
                align="center",
                padding="2",
            ),
            # Task/State Info Section
            task_info_section("Client Token (All Tasks):", DefaultTaskState.client_token),
            task_info_section("Session ID (All Tasks):", DefaultTaskState.session_id),
            task_info_section("Base API Path:", DisplayMonitorState.base_api_path, "bash"),
            
            # API Commands Section
            rx.box(
                rx.vstack(
                    rx.heading("API Commands", size="4"),
                    task_info_section("Get All Tasks Status:", DisplayMonitorState.status_command, 'bash'),
                    task_info_section("Get Single Task Status:", DisplayMonitorState.task_status_command, 'bash'),
                    task_info_section("Start Selected Task:", DisplayMonitorState.start_command, 'bash'),
                    rx.cond(
                        DisplayMonitorState.formatted_curl_body,
                        task_info_section("Task Parameters:", DisplayMonitorState.formatted_curl_body, 'bash'),
                        rx.text("No parameters required for this task"),
                    ),
                    task_info_section("Get Task Result:", DisplayMonitorState.result_command, 'bash'),
                    rx.heading("WebSocket Commands", size="4"),
                    task_info_section("Monitor All Tasks:", DisplayMonitorState.ws_status_command, 'bash'),
                    task_info_section("Monitor Specific Task:", DisplayMonitorState.ws_task_command, 'bash'),
                    padding_x="20",  # Increase this value for more space
                    padding_y="2",  # Increase this value for more space
                    border="1px solid gray",
                    border_radius="md",
                    width="100%",
                ),
                width="100%",
            ),
            rx.button(
                "Start Selected Task",
                # Not stable yet
                on_click=DisplayMonitorState.execute_current_task,
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
                    task_info_section(
                        "Monitor this task:",
                        get_command("ws_task", DEFAULT_STATE_NAME, task_id=task.id)
                    ),
                    padding_y="1",
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
                    task_info_section(
                        "Get task result:",
                        get_command("result", DEFAULT_STATE_NAME, task_id=task.id)
                    ),
                    padding_y="1",
                    width="100%",
                ),
            ),
            width="100%",
        ),
        width="100%",
        height="100%",
        overflow_y="auto",
        padding_x="4",
        padding_y="1",
    )