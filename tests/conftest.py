import os
import pytest
from clerk_backend_api import Clerk
from dotenv import load_dotenv

def load_test_env():
    # Load .env file first
    load_dotenv()
    
    # Then load .env.test if it exists, overriding any duplicate values
    test_env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env.test')
    load_dotenv(test_env_path, override=True)

@pytest.fixture(scope="session")
def load_env():
    load_test_env()
    return {
        "clerk_secret_key": os.getenv("CLERK_SECRET_KEY"),
        "clerk_test_user_id": os.getenv("CLERK_TEST_USER_ID"),
        "api_url": os.getenv("API_URL", "http://localhost:8000")  # Default if not set
    }

@pytest.fixture(scope="session")
def clerk_client(load_env):
    return Clerk(bearer_auth=load_env["clerk_secret_key"])
