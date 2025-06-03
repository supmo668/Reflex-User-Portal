"""Tests for User API endpoints (collection management)"""
import pytest
import requests
import json
from typing import Dict, Any


@pytest.fixture(scope="function")
def auth_headers(load_env, test_token):
    """Get authentication headers for API requests."""
    return {
        'Authorization': f'Bearer {test_token}',
        'Content-Type': 'application/json',
        'Host': load_env.get("host", "http://localhost:3000")
    }


class TestUserCollectionsAPI:
    """Test collection management API endpoints."""
    
    def test_get_user_collections_empty(self, load_env, auth_headers):
        """Test getting collections when user has none."""
        response = requests.get(
            f'{load_env["api_url"]}/api/collections',
            headers=auth_headers,
            timeout=10
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "collections" in data
        assert isinstance(data["collections"], dict)
    
    def test_add_user_collection(self, load_env, auth_headers):
        """Test adding a new collection."""
        collection_data = {
            "description": "Test collection for API testing",
            "entries": {"test_entry": {"data": "test_value"}}
        }
        
        response = requests.post(
            f'{load_env["api_url"]}/api/collections',
            headers=auth_headers,
            json={
                "collection_name": "test_api_collection",
                "collection_data": collection_data
            },
            timeout=10
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "collections" in data
        assert "test_api_collection" in data["collections"]
        assert data["collections"]["test_api_collection"]["description"] == collection_data["description"]
    
    def test_delete_user_collection(self, load_env, auth_headers):
        """Test deleting a collection."""
        # First create a collection to delete
        collection_data = {"description": "Collection to delete", "entries": {}}
        
        create_response = requests.post(
            f'{load_env["api_url"]}/api/collections',
            headers=auth_headers,
            json={
                "collection_name": "delete_test_collection",
                "collection_data": collection_data
            },
            timeout=10
        )
        assert create_response.status_code == 200
        
        # Now delete it
        delete_response = requests.delete(
            f'{load_env["api_url"]}/api/collections/delete_test_collection',
            headers=auth_headers,
            timeout=10
        )
        
        assert delete_response.status_code == 200
        data = delete_response.json()
        assert "delete_test_collection" not in data["collections"]
    
    def test_add_collection_entry(self, load_env, auth_headers):
        """Test adding an entry to a collection."""
        # First create a collection
        collection_data = {"description": "Collection for entry test", "entries": {}}
        
        create_response = requests.post(
            f'{load_env["api_url"]}/api/collections',
            headers=auth_headers,
            json={
                "collection_name": "entry_test_collection",
                "collection_data": collection_data
            },
            timeout=10
        )
        assert create_response.status_code == 200
        
        # Add an entry
        entry_data = {
            "entry_id": "test_entry_1",
            "data": {"name": "Test Entry", "value": 42}
        }
        
        entry_response = requests.post(
            f'{load_env["api_url"]}/api/collections/entry_test_collection/entries',
            headers=auth_headers,
            json=entry_data,
            timeout=10
        )
        
        assert entry_response.status_code == 200
        data = entry_response.json()
        assert "entry_test_collection" in data["collections"]
        collection = data["collections"]["entry_test_collection"]
        assert "test_entry_1" in collection
        assert collection["test_entry_1"]["name"] == "Test Entry"
    
    def test_delete_nonexistent_collection(self, load_env, auth_headers):
        """Test deleting a collection that doesn't exist."""
        response = requests.delete(
            f'{load_env["api_url"]}/api/collections/nonexistent_collection',
            headers=auth_headers,
            timeout=10
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Collection nonexistent_collection not found" in data["detail"]


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
