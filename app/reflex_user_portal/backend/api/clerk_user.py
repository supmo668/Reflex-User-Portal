"""User API endpoints and authentication."""
from typing import Dict, Any
from datetime import datetime, timezone

from sqlmodel import select
from fastapi import FastAPI, Request, HTTPException, status, Depends, APIRouter

# Define the router for this module
router = APIRouter(
    prefix="/api",
    tags=["clerk_user"]
)


import reflex as rx
from clerk_backend_api import Clerk
from clerk_backend_api.models import User as ClerkUser
from clerk_backend_api.jwks_helpers import AuthenticateRequestOptions

from ...models.admin.user import User, UserType, UserModel
from ...utils.logger import get_logger
from ....config import CLERK_AUTHORIZED_DOMAINS, CLERK_SECRET_KEY

# Initialize components
logger = get_logger(__name__)

logger.info("Authorizing domains: %s", CLERK_AUTHORIZED_DOMAINS)
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
        # Log the clerk user object for debugging
        logger.debug("Clerk user object: %s", vars(clerk_user))
        logger.debug("Getting or creating user against Clerk: %s", clerk_user.id)
        
        # Find existing user
        user = session.exec(
            select(User).where(User.clerk_id == clerk_user.id)
        ).first()
        
        if user:
            logger.debug("Found existing user: %s", user)
            return user
        
        # Get primary email safely
        email = None
        if hasattr(clerk_user, 'email_addresses') and clerk_user.email_addresses:
            primary_id = getattr(clerk_user, 'primary_email_address_id', None)
            for email_obj in clerk_user.email_addresses:
                if primary_id and email_obj.id == primary_id:
                    email = email_obj.email_address
                    break
                # If no primary email is set, use the first one
                if not email:
                    email = email_obj.email_address
        
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
        ) from e


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
    """Authenticate a request with Clerk.
    
    Args:
        request: The incoming FastAPI request
        
    Returns:
        ClerkUser: The authenticated Clerk user
        
    Raises:
        HTTPException: If authentication fails or user not found
    """
    # Get the Authorization header for debugging
    auth_header = request.headers.get("Authorization")
    logger.debug("Authorization header: %s", auth_header)
    
    try:
        auth_state = clerk_sdk.authenticate_request(
            request,
            AuthenticateRequestOptions(
                authorized_parties=CLERK_AUTHORIZED_DOMAINS,
            )
        )
        if not auth_state or not auth_state.is_signed_in:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
            
        user_id = auth_state.payload.get('sub')
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User ID not found in token"
            )
            
        user = clerk_sdk.users.get(user_id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found in Clerk"
            )
        return user
            
    except HTTPException as he:
        # Re-raise HTTP exceptions as-is
        raise he
    except Exception as e:
        logger.error("Clerk authentication failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        ) from e


async def get_local_user(request: Request) -> UserModel:
    """FastAPI dependency for user authentication.
    
    Args:
        request: The FastAPI request object
        
    Returns:
        UserModel: The authenticated internal user
        
    Raises:
        HTTPException: If authentication fails
    """
    session = None
    try:
        # First authenticate with Clerk
        clerk_user = await authenticate_clerk_request(request)
        if not clerk_user or not clerk_user.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Clerk user"
            )
            
        # Get or create internal user
        session = rx.session()
        user = get_or_create_user(session, clerk_user)  # Pass the entire clerk_user object
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Failed to create or retrieve local user"
            )
            
        # Update login time
        updated_user = update_user_login(session, user)
        
        # Eager load relationships
        session.refresh(updated_user, ['user_attribute'])
        
        # Convert to dict to avoid detached instance issues
        user_dict = {
            'id': updated_user.id,
            'clerk_id': updated_user.clerk_id,
            'email': updated_user.email,
            'first_name': updated_user.first_name,
            'last_name': updated_user.last_name,
            'user_type': updated_user.user_type,
            'created_at': updated_user.created_at,
            'last_login': updated_user.last_login,
            'is_active': updated_user.is_active,
            'avatar_url': updated_user.avatar_url,
            'user_attribute': {} if updated_user.user_attribute is None else {
                'id': updated_user.user_attribute.id,
                'user_id': updated_user.user_attribute.user_id,
                'collections': updated_user.user_attribute.collections
            }
        }
        
        return UserModel(**user_dict)
            
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error("Authentication failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during authentication"
        ) from e
    finally:
        if session:
            session.close()

@router.get("/users/{user_id}/queries", tags=["users"])
async def get_user_queries_api(
    user_id: int,
    current_user: User = Depends(get_local_user)
) -> Dict[str, Any]:
    """Get user queries by user ID.
    
    Args:
        user_id: The ID of the user to get queries for
        current_user: The authenticated user (injected)
        
    Returns:
        Dict[str, Any]: The user's queries from user_attribute collections
        
    Raises:
        HTTPException: If user not found or unauthorized
    """
    if current_user.id != user_id and current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view these queries"
        )
    
    with rx.session() as session:
        # Eager load user with user_attribute
        user = session.exec(
            rx.select(User).where(User.id == user_id)
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found"
            )
            
        session.refresh(user, ['user_attribute'])
        
        # Get queries from user_attribute collections
        if user.user_attribute and 'queries' in user.user_attribute.collections:
            return user.user_attribute.collections['queries']
        return {}

@router.get("/auth/me", tags=["auth"])
async def get_me(request: Request):
    return await get_local_user(request)

@router.get("/auth/clerk/me", tags=["auth"])
async def get_clerk_me(request: Request):
    return await authenticate_clerk_request(request)

def setup_api(app: FastAPI) -> None:
    """Initialize user-related API routes using APIRouter."""
    logger.info("Initializing user routes")
    app.include_router(router)