# Route templates for consistent path definitions
API_ROUTES = {
    "base": "{prefix}/tasks/{token}",
    "status": "{prefix}/tasks/{token}",
    "status_by_id": "{prefix}/tasks/{token}/{task_id}",
    "start": "{prefix}/tasks/{token}/{session_id}/start/{task_name}",
    "result": "{prefix}/tasks/{token}/{task_id}/result",
    "ws_monitor": "{prefix}/tasks/{token}",
    "ws_task": "{prefix}/tasks/{token}/{task_id}"
}

# Command templates using route templates
API_COMMANDS = {
    "base": "{base_url}{api_prefix}/tasks/{token}",
    "status": "curl -X GET {base_url}{api_prefix}/tasks/{token}",
    "status_by_id": "curl -X GET {base_url}{api_prefix}/tasks/{token}/{task_id}",
    "start": "curl -X POST {base_url}{api_prefix}/tasks/{token}/{session_id}/start/{task_name}",
    "result": "curl -X GET {base_url}{api_prefix}/tasks/{token}/{task_id}/result",
    "ws_all": "wscat -c {ws_url}{ws_prefix}/tasks/{token}",
    "ws_task": "wscat -c {ws_url}{ws_prefix}/tasks/{token}/{task_id}"
}

def get_route(route_type: str, prefix: str, **kwargs) -> str:
    """Get API route with prefix."""
    route_template = API_ROUTES.get(route_type)
    if not route_template:
        raise ValueError(f"Unknown route type: {route_type}")
    return route_template.format(prefix=prefix, **kwargs)

def format_command(command_type: str, state_info: dict, **kwargs) -> str:
    """
    Format API commands using state mappings.
    Args:
        command_type: Type of command to format
        state_name: Name of the state class from STATE_MAPPINGS
        **kwargs: Additional parameters for command formatting
    """
    base_url = kwargs.pop("api_url", "http://localhost:8000")
    ws_url = kwargs.pop("ws_url", "ws://localhost:8000")
    
    command_template = API_COMMANDS.get(command_type)
    if not command_template:
        raise ValueError(f"Unknown command type: {command_type}")

    # Format with state-specific routing
    format_params = {
        "base_url": base_url,
        "ws_url": ws_url,
        "api_prefix": state_info["api_prefix"],
        "ws_prefix": state_info["ws_prefix"],
        **kwargs
    }

    try:
        return command_template.format(**format_params)
    except KeyError as e:
        raise KeyError(f"Missing required parameter: {e} for command type: {command_type}")
