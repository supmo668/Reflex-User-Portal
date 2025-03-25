import os
from typing import List, Dict, Any
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from clerk_backend_api import Clerk
from pydantic import BaseModel

from reflex_user_portal.config import CLERK_SECRET_KEY

clerk_sdk = Clerk(bearer_auth=CLERK_SECRET_KEY)

# Authentication Dependency
async def authenticate_clerk_user(authorization: str = Depends(HTTPBearer())):
    try:
        # Verify the token
        clerk_user = clerk_sdk.users.get_user_by_token(authorization.credentials)
        return clerk_user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication")
