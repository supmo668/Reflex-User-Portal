import os
import pytest
from clerk_backend_api import Clerk
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

def load_test_env():
    # Load .env file first
    load_dotenv()
    
    # Then load .env.test if it exists, overriding any duplicate values
    test_env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env.test')
    load_dotenv(test_env_path, override=True)

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

@pytest.fixture(scope="session")
def load_env():
    load_test_env()
    return {
        "clerk_secret_key": os.getenv("CLERK_SECRET_KEY"),
        "clerk_test_user_id": os.getenv("CLERK_TEST_USER_ID"),
        "api_url": os.getenv("API_URL", "http://localhost:8000"),  # Default if not set
        "admin_email": os.getenv("ADMIN_EMAIL", "admin@example.com"),  # Add admin email
        "host": os.getenv("HOST", "http://localhost:3000")  # Add host
    }

@pytest.fixture(scope="session")
def clerk_client(load_env):
    return Clerk(bearer_auth=load_env["clerk_secret_key"])

@pytest.fixture(scope="function")
def test_token():
    """Get authentication token for testing."""
    return get_test_token_for_user()
