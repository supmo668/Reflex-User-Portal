"""User API endpoints and authentication."""
from typing import Dict, Any, Optional
from sqlmodel import select
from datetime import datetime, timezone
from fastapi import Request, HTTPException, status, Depends
from pydantic import BaseModel

import reflex as rx
from clerk_backend_api import Clerk
from clerk_backend_api.models import User as ClerkUser
from clerk_backend_api.jwks_helpers import AuthenticateRequestOptions

from reflex_user_portal.models.user import User, UserType, UserModel
from reflex_user_portal.utils.logger import get_logger
from reflex_user_portal.config import CLERK_AUTHORIZED_DOMAINS, CLERK_SECRET_KEY

# Initialize components
logger = get_logger(__name__)

# Initialize Clerk SDK
if not CLERK_SECRET_KEY:
    raise ValueError("CLERK_SECRET_KEY environment variable is not set")

clerk_sdk = Clerk(bearer_auth=CLERK_SECRET_KEY)


def get_or_create_user(session: rx.session, clerk_user: ClerkUser) -> User:
    """Get or create a user from Clerk data.
    
    Args:
        session: The database session
        clerk_user: The Clerk user object
        
    Returns:
        User: The internal user model
        
    Raises:
        HTTPException: If there's an error creating/getting the user
    """
    try:
        logger.debug("Getting or creating user against Clerk: %s", clerk_user.id)
        # Find existing user
        user = session.exec(
            select(User).where(User.clerk_id == clerk_user.id)
        ).first()
        
        if user:
            logger.debug("Found existing user: %s", user)
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
        logger.error("Error in get_or_create_user: %s", e)
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
            user = clerk_sdk.users.get(user_id=auth_state.payload.get('sub'))
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found in Clerk"
                )
            return user
    except Exception as e:
        logger.error("Clerk authentication failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


async def get_local_user(
    clerk_user: ClerkUser = Depends(authenticate_clerk_request),
) -> UserModel:
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
            user = get_or_create_user(session, clerk_user.id)
            return update_user_login(session, user)
            
    except Exception as e:
        logger.error(f"Authentication failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

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
    app.api.add_api_route("/api/auth/me", get_local_user, methods=["GET"])
    app.api.add_api_route("/api/auth/clerk/me", authenticate_clerk_request, methods=["GET"])