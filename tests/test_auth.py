import pytest
import requests
import os
from clerk_backend_api import Clerk

import logging

logger = logging.getLogger(__name__)
def get_test_token_for_user() -> str:
    """Helper function to get test token"""
    try:
        with Clerk(
            bearer_auth=os.getenv("CLERK_SECRET_KEY"),
        ) as clerk:

            res = clerk.testing_tokens.create()

            assert res is not None

            # Handle response
            print(f"Response attributes: {vars(res).keys()}")
            return res.token
            
    except Exception as e:
        pytest.fail(f"Error obtaining token: {e}")
        return None

class TestAuth:
    """Group authentication related tests"""
    
    def test_auth_me_endpoint(self, load_env):
        """Test the /api/auth/me endpoint"""
        # Get token for admin user
        token: str = get_test_token_for_user()
        assert token is not None, "Failed to obtain authentication token"
        # Test the /api/auth/me endpoint using API_URL from environment
        response = requests.get(
            f'{load_env["api_url"]}/api/auth/me',
            headers={
                'Authorization': f'Bearer {token}',
                'Host': "http://localhost:3000"
            },
            timeout=10
        )
        data = response.json()
        assert response.status_code == 200, f"Authentication request failed: {data}"
        assert "id" in data, "Response should contain user ID"
        assert data["email"] == load_env["admin_email"], "Email in response doesn't match"

if __name__ == "__main__":
    pytest.main([__file__])
