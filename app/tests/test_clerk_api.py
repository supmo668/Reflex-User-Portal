"""Tests for Clerk User API endpoints (authentication)"""
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


class TestClerkAuthAPI:
    """Test Clerk authentication API endpoints."""
    
    def test_auth_me_endpoint(self, load_env, auth_headers):
        """Test the /api/auth/me endpoint for getting current user."""
        response = requests.get(
            f'{load_env["api_url"]}/api/auth/me',
            headers=auth_headers,
            timeout=10
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "email" in data
        assert "clerk_id" in data
        assert "user_type" in data
        
    def test_auth_clerk_me_endpoint(self, load_env, auth_headers):
        """Test the /api/auth/clerk/me endpoint for getting Clerk user data."""
        response = requests.get(
            f'{load_env["api_url"]}/api/auth/clerk/me',
            headers=auth_headers,
            timeout=10
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "email_addresses" in data
        
    def test_get_user_queries_self(self, load_env, auth_headers):
        """Test getting user queries for self."""
        # First get current user ID
        me_response = requests.get(
            f'{load_env["api_url"]}/api/auth/me',
            headers=auth_headers,
            timeout=10
        )
        assert me_response.status_code == 200
        user_id = me_response.json()["id"]
        
        # Get user queries
        response = requests.get(
            f'{load_env["api_url"]}/api/users/{user_id}/queries',
            headers=auth_headers,
            timeout=10
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)  # Should return queries dict
        
    def test_unauthorized_request(self, load_env):
        """Test making request without authorization token."""
        response = requests.get(
            f'{load_env["api_url"]}/api/auth/me',
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        assert response.status_code == 401
        
    def test_invalid_token(self, load_env):
        """Test making request with invalid authorization token."""
        headers = {
            'Authorization': 'Bearer invalid_token',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            f'{load_env["api_url"]}/api/auth/me',
            headers=headers,
            timeout=10
        )
        
        assert response.status_code == 401


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
