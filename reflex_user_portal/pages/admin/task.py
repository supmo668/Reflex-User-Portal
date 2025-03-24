import os

import reflex as rx
from reflex_user_portal.templates import portal_template
from reflex_user_portal.backend.states.task import DisplayMonitorState
from reflex_user_portal.backend.states.task.example_task import ExampleTaskState

# Command templates - makes it easier to maintain and more efficient
API_COMMANDS = {
    "base": "{api_url}/tasks/{token}",
    "status": "curl -X GET {base_path}",
    "status_by_id": "curl -X GET {base_path}/{task_id}",
    "start": "curl -X POST {base_path}/start/{task_function}",
    "result": "curl -X GET {base_path}/{task_id}/result",
    "ws_all": "wscat -c {ws_url}/tasks/{token}",
    "ws_task": "wscat -c {ws_url}/tasks/{token}/{task_id}"
}

@portal_template(route="/admin/tasks", title="Task Dashboard")
def task_status_display():
    """Display the status of tasks."""
    API_URL = os.getenv("API_URL", "http://localhost:8000/api")
    WS_URL = os.getenv("WS_URL", "ws://localhost:8000/ws")
    BASE_API_PATH = f"{API_URL}/tasks/{ExampleTaskState.client_token}"
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
                API_COMMANDS["base"].format(
                    api_url=API_URL,
                    state_prefix=DisplayMonitorState.current_state_prefix,
                    token=ExampleTaskState.client_token
                ),
                language="bash",
                can_copy=True
            ),
            # API Commands Section
            rx.box(
                rx.vstack(
                    rx.heading("API Commands", size="4"),
                    rx.text("Get All Tasks Status:"),
                    rx.code_block(
                        API_COMMANDS["status"].format(
                            base_path=BASE_API_PATH
                        ),
                        language="bash",
                        can_copy=True
                    ),
                    
                    rx.text("Get Single Task Status:"),
                    rx.code_block(
                        API_COMMANDS["status_by_id"].format(
                            base_path=BASE_API_PATH,
                            task_id="{task_id}"
                        ),
                        language="bash",
                        can_copy=True
                    ),
                    
                    rx.text("Start Selected Task:"),
                    rx.code_block(
                        API_COMMANDS["start"].format(
                            base_path=BASE_API_PATH,
                            task_function=ExampleTaskState.current_task_function
                        ),
                        language="bash",
                        can_copy=True
                    ),
                    
                    rx.text("Get Task Result:"),
                    rx.code_block(
                        API_COMMANDS["result"].format(
                            base_path=BASE_API_PATH,
                            task_id="{task_id}"
                        ),
                        language="bash",
                        can_copy=True
                    ),
                    
                    rx.heading("WebSocket Commands", size="4"),
                    rx.text("Monitor All Tasks:"),
                    rx.code_block(
                        API_COMMANDS["ws_all"].format(
                            ws_url=WS_URL,
                            state_prefix=DisplayMonitorState.current_state_prefix,
                            token=ExampleTaskState.client_token
                        ),
                        language="bash",
                        can_copy=True
                    ),
                    
                    rx.text("Monitor Specific Task:"),
                    rx.code_block(
                        API_COMMANDS["ws_task"].format(
                            ws_url=WS_URL,
                            state_prefix=DisplayMonitorState.current_state_prefix,
                            token=ExampleTaskState.client_token,
                            task_id="{task_id}"
                        ),
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
                        API_COMMANDS["ws_task"].format(
                            ws_url=WS_URL,
                            state_prefix=DisplayMonitorState.current_state_prefix,
                            token=ExampleTaskState.client_token,
                            task_id=task.id
                        ),
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
                        API_COMMANDS["result"].format(
                            base_path=BASE_API_PATH,
                            task_id=task.id
                        ),
                        language="bash",
                        can_copy=True,
                    ),
                    padding="2",
                ),
            ),
            spacing="4",
        )
    )
