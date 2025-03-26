import os
from typing import Type

import reflex as rx


from reflex_user_portal.templates import portal_template
from reflex_user_portal.backend.states.task import DisplayMonitorState, STATE_MAPPINGS, MonitorState
from reflex_user_portal.backend.api.commands import format_command

@portal_template(route="/admin/tasks", title="Task Dashboard")
def task_status_display():
    """Display the status of tasks."""
    ExampleTaskState: Type[MonitorState] = STATE_MAPPINGS["ExampleTaskState"].get("cls")
    def get_command(cmd_type: str, state_name: str="ExampleTaskState", **kwargs) -> str:
        """Helper to format commands with current state info"""
        state_info = STATE_MAPPINGS[state_name]
        return format_command(
            cmd_type,
            state_info,
            client_token=ExampleTaskState.client_token,
            **kwargs
        )
    
    return rx.center(
        rx.vstack(
            rx.heading("Task Monitor"),
            rx.hstack(
                rx.text("State Type: (Simulated)"),
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
            ),
            rx.text("Client Token (Example Task): "),
            rx.code_block(ExampleTaskState.client_token, can_copy=True),
            rx.text("Session ID (Example Task): "), rx.code_block(ExampleTaskState.session_id, can_copy=True),
            rx.text("Base API Path:"),
            rx.code_block(
                DisplayMonitorState.base_api_path,
                language="bash",
                can_copy=True
            ),
            # API Commands Section
            rx.box(
                rx.vstack(
                    rx.heading("API Commands", size="4"),
                    rx.text("Get All Tasks Status:"),
                    rx.code_block(
                        DisplayMonitorState.status_command,
                        language="bash",
                        can_copy=True
                    ),
                    rx.text("Get Single Task Status:"),
                    rx.code_block(
                        DisplayMonitorState.task_status_command,
                        language="bash",
                        can_copy=True
                    ),
                    rx.text("Start Selected Task:"),
                    rx.code_block(
                        DisplayMonitorState.start_command,
                        language="bash",
                        can_copy=True
                    ),
                    rx.text("Get Task Result:"),
                    rx.code_block(
                        DisplayMonitorState.result_command,
                        language="bash",
                        can_copy=True
                    ),
                    rx.heading("WebSocket Commands", size="4"),
                    rx.text("Monitor All Tasks:"),
                    rx.code_block(
                        DisplayMonitorState.ws_status_command,
                        language="bash",
                        can_copy=True
                    ),
                    rx.text("Monitor Specific Task:"),
                    rx.code_block(
                        DisplayMonitorState.ws_task_command,
                        language="bash",
                        can_copy=True
                    ),
                    padding="4",
                    border="1px solid",
                    border_radius="md",
                ),
                padding="4",
                border="1px solid",
            ),
            rx.button(
                "Start Selected Task",
                on_click=ExampleTaskState.long_running_task,
            ),
            rx.divider(),
            
            # Active Tasks Section
            rx.heading("Active Tasks (Simulated Example)"),
            rx.foreach(
                ExampleTaskState.active_tasks,
                lambda task: rx.vstack(
                    rx.heading(task.name, size="2"),
                    rx.text(f"Task ID: {task.id}"),
                    rx.text(f"Status: {task.status}"),
                    rx.progress(value=task.progress, max=100),
                    rx.text("Monitor this task:"),
                    rx.code_block(
                        get_command("ws_task", "ExampleTaskState", task_id=task.id),
                        language="bash", can_copy=True,
                    ),
                    padding="2",
                )
            ),
            
            # Completed Tasks Section
            rx.heading("Completed Tasks (Simulated Example)"),
            rx.foreach(
                ExampleTaskState.completed_tasks,
                lambda task: rx.vstack(
                    rx.heading(task.name),
                    rx.text(f"Status: {task.status}"),
                    rx.text(f"Task ID: {task.id}"),
                    rx.text("Get task result:"),
                    rx.code_block(
                        get_command("result", "ExampleTaskState", task_id=task.id),
                        language="bash", can_copy=True,
                    ),
                    padding="2",
                ),
            ),
            spacing="4",
        )
    )
