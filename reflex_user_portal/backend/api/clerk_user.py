"""User API endpoints and authentication."""
from typing import Dict, Any, Optional
import os
from datetime import datetime, timezone
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from clerk_backend_api import Clerk, User as ClerkUser
from clerk_backend_api.jwks_helpers import AuthenticateRequestOptions
import reflex as rx

from reflex_user_portal.models.user import User, UserType, UserAPI
from reflex_user_portal.utils.logger import get_logger
from reflex_user_portal.config import CLERK_AUTHORIZED_DOMAINS

# Initialize components
logger = get_logger(__name__)
auth_scheme = HTTPBearer()

# Initialize Clerk SDK
clerk_secret_key = os.getenv('CLERK_SECRET_KEY')
if not clerk_secret_key:
    raise ValueError("CLERK_SECRET_KEY environment variable is not set")

clerk_sdk = Clerk(bearer_auth=clerk_secret_key)

# Response models
class AuthStatus(BaseModel):
    """Authentication status model."""
    authenticated: bool
    message: str
    user_id: Optional[int] = None
    clerk_id: Optional[str] = None

def get_or_create_user(session: rx.session, clerk_user: ClerkUser) -> User:
    """Get or create a user from Clerk data.
    
    Args:
        session: The database session
        clerk_user: The Clerk user data
        
    Returns:
        User: The internal user model
        
    Raises:
        HTTPException: If there's an error creating/getting the user
    """
    try:
        # Find existing user
        user = session.exec(
            rx.select(User).where(User.clerk_id == clerk_user.user_id)
        ).first()
        
        if user:
            return user
        
        # Get primary email
        email = clerk_user.email_addresses[0].email_address if clerk_user.email_addresses else None
        
        # Create new user
        user = User(
            clerk_id=clerk_user.id,
            email=email,
            first_name=getattr(clerk_user, 'first_name', None),
            last_name=getattr(clerk_user, 'last_name', None),
            user_type=UserType.USER,
            created_at=datetime.now(timezone.utc)
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        
        return user
        
    except Exception as e:
        logger.error(f"Error in get_or_create_user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating/getting user: {str(e)}"
        )


def update_user_login(session: rx.session, user: User) -> User:
    """Update user's last login time.
    
    Args:
        session: The database session
        user: The user to update
        
    Returns:
        User: The updated user
    """
    user.last_login = datetime.now(timezone.utc)
    session.commit()
    session.refresh(user)
    return user


async def authenticate_clerk_request(request: Request) -> ClerkUser:
    """Authenticate a request with Clerk."""
    try:
        auth_state = clerk_sdk.authenticate_request(
            request,
            AuthenticateRequestOptions(
                authorized_parties=CLERK_AUTHORIZED_DOMAINS,
            )
        )
        if auth_state.is_signed_in:
            user = clerk_sdk.users.get_user(auth_state.session.user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found in Clerk"
                )
            return user
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not signed in"
            )
    except Exception as e:
        logger.error(f"Clerk authentication failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


async def get_local_user(
    clerk_user: ClerkUser = Depends(authenticate_clerk_request),
) -> User:
    """FastAPI dependency for user authentication.
    
    Args:
        credentials: The HTTP bearer credentials
        request: Optional FastAPI request
        
    Returns:
        User: The authenticated internal user
        
    Raises:
        HTTPException: If authentication fails
    """
    try:        
        # Get or create internal user
        with rx.session() as session:
            user = get_or_create_user(session, clerk_user)
            return update_user_login(session, user)
            
    except Exception as e:
        logger.error(f"Authentication failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    
async def verify_token_api(
    user: User = Depends(get_local_user)
) -> AuthStatus:
    """Verify the authentication token and return the authentication status."""
    return AuthStatus(
        authenticated=True,
        message="Authentication successful",
        user_id=user.id,
        clerk_id=user.clerk_id
    )

async def get_current_user_api(
    user: User = Depends(get_local_user)
) -> UserAPI:
    """Get current authenticated user."""
    return UserAPI.from_user(user)

async def get_user_queries_api(
    user_id: int,
    current_user: User = Depends(get_local_user)
) -> Dict[str, Any]:
    """Get user queries by user ID.
    
    Args:
        user_id: The ID of the user to get queries for
        current_user: The authenticated user (injected)
        
    Returns:
        Dict[str, Any]: The user's queries
        
    Raises:
        HTTPException: If user not found or unauthorized
    """
    if current_user.id != user_id and current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view these queries"
        )
    
    with rx.session() as session:
        user = session.exec(
            rx.select(User).where(User.id == user_id)
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found"
            )
        
        return user.user_queries.queries if user.user_queries else {}

def setup_api(app: rx.App) -> None:
    """Initialize user-related API routes.
    
    Args:
        app: The Reflex application
    """
    logger.info("Initializing user routes")
    
    # User data routes
    app.api.add_api_route("/api/users/{user_id}/queries", get_user_queries_api, methods=["GET"])
    
    # Authentication route
    app.api.add_api_route("/api/auth/me", get_current_user_api, methods=["GET"])