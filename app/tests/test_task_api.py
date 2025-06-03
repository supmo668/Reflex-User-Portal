"""Tests for Task API endpoints using example_task2 state"""
import pytest
import requests
import json
import time
import asyncio
import websockets
from typing import Dict, Any
import uuid


@pytest.fixture(scope="function")
def client_token():
    """Generate a unique client token for testing."""
    return str(uuid.uuid4())[:12]


@pytest.fixture(scope="session")
def task_api_base_url(load_env):
    """Get the task API base URL."""
    return f"{load_env['api_url']}/api/example_task2"


class TestTaskAPI:
    """Test Task API endpoints for example_task2 state."""
    
    def test_start_task1(self, task_api_base_url, client_token):
        """Test starting task1 (no parameters)."""
        endpoint = f"{task_api_base_url}/tasks/{client_token}/start/task1"
        
        response = requests.post(
            endpoint,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        return data["task_id"]
    
    def test_start_task2_with_args(self, task_api_base_url, client_token):
        """Test starting task2_with_args with parameters."""
        endpoint = f"{task_api_base_url}/tasks/{client_token}/start/task2_with_args"
        
        test_data = {
            "name": "TestUser",
            "age": 30
        }
        
        response = requests.post(
            endpoint,
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        return data["task_id"]
    
    def test_get_task_status(self, task_api_base_url, client_token):
        """Test getting task status."""
        # First start a task
        task_id = self.test_start_task1(task_api_base_url, client_token)
        
        # Get task status
        status_endpoint = f"{task_api_base_url}/tasks/{client_token}/{task_id}"
        
        response = requests.get(status_endpoint, timeout=10)
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data
        assert "status" in data
        assert "progress" in data
        assert data["id"] == task_id
    
    def test_get_all_tasks_status(self, task_api_base_url, client_token):
        """Test getting all tasks status."""
        # Start a task first
        self.test_start_task1(task_api_base_url, client_token)
        
        # Get all tasks status
        status_endpoint = f"{task_api_base_url}/tasks/{client_token}"
        
        response = requests.get(status_endpoint, timeout=10)
        assert response.status_code == 200
        
        data = response.json()
        assert "all_tasks" in data
        assert isinstance(data["all_tasks"], dict)
    
    def test_get_task_result_completed(self, task_api_base_url, client_token):
        """Test getting task result after completion."""
        # Start a task
        task_id = self.test_start_task1(task_api_base_url, client_token)
        
        # Wait for task to complete (with timeout)
        status_endpoint = f"{task_api_base_url}/tasks/{client_token}/{task_id}"
        max_retries = 15
        
        for _ in range(max_retries):
            status_response = requests.get(status_endpoint, timeout=10)
            assert status_response.status_code == 200
            
            status_data = status_response.json()
            if status_data.get("status") == "Completed":
                break
            time.sleep(1)
        
        # Get task result
        result_endpoint = f"{task_api_base_url}/tasks/{client_token}/result/{task_id}"
        result_response = requests.get(result_endpoint, timeout=10)
        
        assert result_response.status_code == 200
        result_data = result_response.json()
        # task1 should return "<Task1 Result>"
        assert result_data == "<Task1 Result>"
    
    def test_task2_with_args_result(self, task_api_base_url, client_token):
        """Test task2_with_args returns the input parameters."""
        test_data = {
            "name": "TestUser",
            "age": 30
        }
        
        # Start task with parameters
        task_id = self.test_start_task2_with_args(task_api_base_url, client_token)
        
        # Wait for completion
        status_endpoint = f"{task_api_base_url}/tasks/{client_token}/{task_id}"
        max_retries = 15
        
        for _ in range(max_retries):
            status_response = requests.get(status_endpoint, timeout=10)
            assert status_response.status_code == 200
            
            status_data = status_response.json()
            if status_data.get("status") == "Completed":
                break
            time.sleep(1)
        
        # Get result
        result_endpoint = f"{task_api_base_url}/tasks/{client_token}/result/{task_id}"
        result_response = requests.get(result_endpoint, timeout=10)
        
        assert result_response.status_code == 200
        result_data = result_response.json()
        assert result_data["name"] == test_data["name"]
        assert result_data["age"] == test_data["age"]
    
    def test_nonexistent_task(self, task_api_base_url, client_token):
        """Test starting a task that doesn't exist."""
        endpoint = f"{task_api_base_url}/tasks/{client_token}/start/nonexistent_task"
        
        response = requests.post(
            endpoint,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        assert response.status_code == 404
    
    def test_task_result_not_completed(self, task_api_base_url, client_token):
        """Test getting result of task that hasn't completed."""
        # Start a task but don't wait for completion
        task_id = self.test_start_task1(task_api_base_url, client_token)
        
        # Immediately try to get result
        result_endpoint = f"{task_api_base_url}/tasks/{client_token}/result/{task_id}"
        result_response = requests.get(result_endpoint, timeout=10)
        
        # Should return error since task isn't completed yet
        assert result_response.status_code == 400


class TestDirectTaskAPI:
    """Test Direct Task API endpoints."""
    
    def test_direct_start_task1(self, task_api_base_url):
        """Test direct execution of task1."""
        endpoint = f"{task_api_base_url}/task/start/task1"
        
        response = requests.post(
            endpoint,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        return data["task_id"]
    
    def test_direct_start_task2_with_args(self, task_api_base_url):
        """Test direct execution of task2_with_args."""
        endpoint = f"{task_api_base_url}/task/start/task2_with_args"
        
        test_data = {
            "name": "DirectTestUser",
            "age": 25
        }
        
        response = requests.post(
            endpoint,
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        return data["task_id"]
    
    def test_direct_get_result(self, task_api_base_url):
        """Test getting result of directly executed task."""
        # Start a direct task
        task_id = self.test_direct_start_task1(task_api_base_url)
        
        # Wait and get result
        time.sleep(5)  # Direct tasks should complete quickly
        
        result_endpoint = f"{task_api_base_url}/task/result/{task_id}"
        response = requests.get(result_endpoint, timeout=10)
        
        assert response.status_code == 200
        data = response.json()
        assert "result" in data


@pytest.mark.asyncio
class TestTaskWebSocket:
    """Test WebSocket endpoints for task monitoring."""
    
    async def test_websocket_task_monitoring(self, task_api_base_url, client_token):
        """Test WebSocket monitoring of task progress."""
        # Start a task first
        start_endpoint = f"{task_api_base_url.replace('http://', '')}/tasks/{client_token}/start/task1"
        response = requests.post(f"http://{start_endpoint}", timeout=10)
        task_id = response.json()["task_id"]
        
        # Connect to WebSocket
        ws_uri = f"ws://{task_api_base_url.replace('http://', '')}/task/ws/{task_id}"
        
        try:
            async with websockets.connect(ws_uri) as websocket:
                # Receive messages for a short time
                for _ in range(5):
                    message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    data = json.loads(message)
                    assert "type" in data
                    assert "data" in data
                    
                    if data["type"] == "status_update":
                        assert "status" in data["data"]
                        assert "progress" in data["data"]
        except (websockets.exceptions.ConnectionClosed, asyncio.TimeoutError):
            # This is expected for testing
            pass


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
