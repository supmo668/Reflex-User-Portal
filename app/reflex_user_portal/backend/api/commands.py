import os

# Base command patterns
HTTP_CMD_PATTERN = {
    "GET": "curl -X GET {base_url}{route}",
    "POST": "curl -X POST -H \"Content-Type: application/json\" {base_url}{route}",
    "WS": "wscat -c {ws_url}{route}"
}

# API Route templates for consistent path definitions that create routes
API_ROUTES = {
    "base": "{prefix}/tasks/{client_token}",
    "token": "{prefix}/token",
    "status": "{prefix}/tasks/{client_token}",
    "status_by_id": "{prefix}/tasks/{client_token}/{task_id}",
    "start": "{prefix}/tasks/{client_token}/start/{task_name}",
    "result": "{prefix}/tasks/{client_token}/result/{task_id}",
    "ws_monitor": "{prefix}/tasks/{client_token}",
    "ws_task": "{prefix}/tasks/{client_token}/{task_id}"
}

# Command templates using route patterns for display in MonitorState
API_COMMANDS = {
    "base": "{base_url}" + API_ROUTES["base"],
    "status": ("GET", API_ROUTES["status"]),
    "status_by_id": ("GET", API_ROUTES["status_by_id"]),
    "start": ("POST", API_ROUTES["start"]),
    "result": ("GET", API_ROUTES["result"]),
    "ws_all": ("WS", API_ROUTES["ws_monitor"]),
    "ws_task": ("WS", API_ROUTES["ws_task"]),
    "create_token": ("GET", API_ROUTES["token"])
}

def get_route(route_type: str, prefix: str, client_token: str="{client_token}", task_id: str="{task_id}", **kwargs) -> str:
    """
    Get API route with prefix. Format the route template with the prefix and kwargs.
    """
    route_template = API_ROUTES.get(route_type)
    if not route_template:
        raise ValueError(f"Unknown route type: {route_type}")
    return route_template.format(prefix=prefix, client_token=client_token, task_id=task_id, **kwargs)

def format_command(command_type: str, state_info: dict, **kwargs) -> str:
    """
    Format API commands using state mappings.
    Args:
        command_type: Type of command to format
        state_info: Dictionary containing api_prefix and ws_prefix
        **kwargs: Additional parameters for command formatting
    """
    API_URL = os.getenv("API_URL", "http://localhost:8000")
    WS_URL = os.getenv("WS_URL", API_URL.replace("http://", "ws://"))
    command_template = API_COMMANDS.get(command_type)
    if not command_template:
        raise ValueError(f"Unknown command type: {command_type}")

    # Format with prefix-specific routing
    prefix = state_info.get("api_prefix", "/api")
    if command_type.startswith("ws_"):
        prefix = state_info.get("ws_prefix", "/ws")

    # Special handling for base command
    if command_type == "base":
        return command_template.format(base_url=API_URL, prefix=prefix, **kwargs)

    # For other commands, format the route first, then the command pattern
    method, route_template = command_template
    route = route_template.format(prefix=prefix, **kwargs)
    
    format_params = {
        "base_url": API_URL,
        "ws_url": WS_URL,
        "route": route
    }

    return HTTP_CMD_PATTERN[method].format(**format_params)
