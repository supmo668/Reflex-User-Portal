import os
import pytest
import requests
import json
import time
import uuid

from app.reflex_user_portal.backend.states.task.example_task2.model import InputArgs


@pytest.fixture(scope="function")
def client_token():
    """Generate a unique client token for testing."""
    return str(uuid.uuid4())[:12]


@pytest.fixture(scope="session")
def api_base_url(load_env):
    """Get the base API URL from environment or use default."""
    return f"{load_env['api_url']}/api/example_task2/tasks"


def test_task2_with_args(api_base_url, client_token):
    """Test the task2_with_args endpoint with InputArgs payload."""
    # Endpoint for starting the task
    endpoint = f"{api_base_url}/{client_token}/start/task2_with_args"
    
    # Create test data based on InputArgs model
    test_data = {
        "name": "TestUser",
        "age": 30
    }
    
    # Make the POST request
    response = requests.post(
        endpoint,
        json=test_data,
        headers={"Content-Type": "application/json"}
    )
    
    # Check response
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    # Parse response to get task ID
    response_data = response.json()
    assert "task_id" in response_data, "Response should contain task_id"
    task_id = response_data["task_id"]
    
    # Check task status
    status_endpoint = f"{api_base_url}/{client_token}/status/{task_id}"
    
    # Wait for task to complete (with timeout)
    max_retries = 10
    for _ in range(max_retries):
        status_response = requests.get(status_endpoint)
        assert status_response.status_code == 200
        
        status_data = status_response.json()
        if status_data.get("status") == "COMPLETED":
            break
            
        # Wait before checking again
        time.sleep(1)
    
    # Get final result
    result_endpoint = f"{api_base_url}/{client_token}/result/{task_id}"
    result_response = requests.get(result_endpoint)
    assert result_response.status_code == 200
    
    # Verify result contains our input data
    result_data = result_response.json()
    assert result_data.get("name") == test_data["name"]
    assert result_data.get("age") == test_data["age"]
    
    print(f"Task completed successfully with result: {result_data}")
    return result_data


if __name__ == "__main__":
    # This allows running the test directly with python
    pytest.main(["-xvs", __file__])
