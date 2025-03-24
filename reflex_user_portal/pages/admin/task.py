import os

import reflex as rx
from reflex_user_portal.templates import portal_template
from reflex_user_portal.backend.states.task import DisplayMonitorState, STATE_MAPPINGS
from reflex_user_portal.backend.api.commands import format_command

@portal_template(route="/admin/tasks", title="Task Dashboard")
def task_status_display():
    """Display the status of tasks."""
    API_URL = os.getenv("API_URL", "http://localhost:8000")
    WS_URL = os.getenv("WS_URL", "ws://localhost:8000")
    
    def get_command(cmd_type: str, **kwargs) -> str:
        """Helper to format commands with current state info"""
        # state_info = STATE_MAPPINGS[DisplayMonitorState.current_state_type]
        state_info = STATE_MAPPINGS["ExampleTaskState"]
        return format_command(
            cmd_type,
            state_info,
            api_url=API_URL,
            ws_url=WS_URL,
            token=ExampleTaskState.client_token,
            **kwargs
        )
    ExampleTaskState = STATE_MAPPINGS["ExampleTaskState"].get("cls")
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
                            lambda item: rx.select.item(item[1], value=item[0])
                        )
                    ),
                    value=DisplayMonitorState.current_task_function,
                    on_change=DisplayMonitorState.change_task_function,
                ),
            ),
            rx.text("Client Token: ", ExampleTaskState.client_token),
            rx.text("Base API Path:"),
            rx.code_block(
                get_command("base"),
                language="bash",
                can_copy=True
            ),
            
            # API Commands Section
            rx.box(
                rx.vstack(
                    rx.heading("API Commands", size="4"),
                    rx.text("Get All Tasks Status:"),
                    rx.code_block(
                        get_command("status"),
                        language="bash",
                        can_copy=True
                    ),
                    
                    rx.text("Get Single Task Status:"),
                    rx.code_block(
                        get_command("status_by_id", task_id="{task_id}"),
                        language="bash",
                        can_copy=True
                    ),
                    
                    rx.text("Start Selected Task:"),
                    rx.code_block(
                        get_command(
                            "start",
                            session_id="{session_id}",
                            task_name=DisplayMonitorState.current_task_function  # Changed from task_function to task_name
                        ),
                        language="bash",
                        can_copy=True
                    ),
                    
                    rx.text("Get Task Result:"),
                    rx.code_block(
                        get_command("result", task_id="{task_id}"),
                        language="bash",
                        can_copy=True
                    ),
                    
                    rx.heading("WebSocket Commands", size="4"),
                    rx.text("Monitor All Tasks:"),
                    rx.code_block(
                        get_command("ws_all"),  # Changed from ws_all to ws_monitor
                        language="bash",
                        can_copy=True
                    ),
                    
                    rx.text("Monitor Specific Task:"),
                    rx.code_block(
                        get_command("ws_task", task_id="{task_id}"),
                        language="bash",
                        can_copy=True
                    ),
                    padding="4",
                    border="1px solid",
                    border_radius="md",
                ),
            ),
            
            rx.button(
                "Start Selected Task (Simulated)",
                on_click=ExampleTaskState.long_running_task,
                color_scheme="green",
            ),
            rx.divider(),
            
            # Active Tasks Section
            rx.heading("Active Tasks"),
            rx.foreach(
                ExampleTaskState.active_tasks,
                lambda task: rx.vstack(
                    rx.heading(task.name, size="2"),
                    rx.text(f"Task ID: {task.id}"),
                    rx.text(f"Status: {task.status}"),
                    rx.progress(value=task.progress, max=100),
                    rx.text("Monitor this task:"),
                    rx.code_block(
                        get_command("ws_task", task_id=task.id),
                        language="bash",
                        can_copy=True,
                    ),
                    padding="2",
                )
            ),
            
            # Completed Tasks Section
            rx.heading("Completed Tasks"),
            rx.foreach(
                ExampleTaskState.completed_tasks,
                lambda task: rx.vstack(
                    rx.heading(task.name),
                    rx.text(f"Status: {task.status}"),
                    rx.text(f"Task ID: {task.id}"),
                    rx.text("Get task result:"),
                    rx.code_block(
                        get_command("result", task_id=task.id),
                        language="bash",
                        can_copy=True,
                    ),
                    padding="2",
                ),
            ),
            spacing="4",
        )
    )
