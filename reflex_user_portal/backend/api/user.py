"""User API endpoints and collection management functionality"""
from typing import Dict, Optional, Tuple, Any
from fastapi import HTTPException, status, Depends

import reflex as rx
from sqlmodel import select, Session

from reflex_user_portal.models import (
    User, 
    UserAttribute,
    CollectionResponse
)
from reflex_user_portal.backend.api.clerk_user import get_local_user


def get_user_attribute(session: Session, user_id: int) -> Tuple[UserAttribute, bool]:
    """Get or create user attribute for a user.
    
    Args:
        session: Database session
        user_id: User ID
        
    Returns:
        Tuple of (UserAttribute, bool) where bool indicates if it was created
    
    Raises:
        HTTPException: If user not found
    """
    user_attr = session.exec(
        select(UserAttribute).where(UserAttribute.user_id == user_id)
    ).first()
    
    if not user_attr:
        user = session.exec(select(User).where(User.id == user_id)).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        user_attr = UserAttribute(user_id=user_id, user_collections={})
        session.add(user_attr)
        return user_attr, True
    
    return user_attr, False


def get_collection(user_attr: UserAttribute, collection_name: str) -> Optional[Dict]:
    """Get a collection by name.
    
    Args:
        user_attr: User attribute object
        collection_name: Name of the collection
        
    Returns:
        Collection if found, None otherwise
    """
    return user_attr.collections.get(collection_name)


# API Endpoints
def get_user_collections_core(session: Session, user_id: int) -> Dict:
    """Get all collections for a user - core function"""
    user_attr, _ = get_user_attribute(session, user_id)
    return user_attr.collections

async def get_user_collections(
    current_user: User = Depends(get_local_user)
) -> CollectionResponse:
    """Get all collections for a user - API endpoint"""
    with rx.session() as session:
        collections = get_user_collections_core(session, current_user.id)
        return CollectionResponse(collections=collections)


def add_user_collection_core(session: Session, user_id: int, collection_name: str, collection_data: Dict[str, Any]) -> Dict:
    """Add a new collection for a user - core function"""
    user_attr, is_new = get_user_attribute(session, user_id)
    collections = dict(user_attr.collections)  # Create a new dict
    collections[collection_name] = collection_data
    user_attr.collections = collections  # Reassign to trigger change tracking
    session.commit()
    session.refresh(user_attr)
    return user_attr.collections

async def add_user_collection(
    collection_name: str,
    collection_data: Dict[str, Any],
    current_user: User = Depends(get_local_user)
) -> CollectionResponse:
    """Add a new collection for a user - API endpoint"""
    with rx.session() as session:
        collections = add_user_collection_core(session, current_user.id, collection_name, collection_data)
        return CollectionResponse(collections=collections)


def delete_user_collection_core(session: Session, user_id: int, collection_name: str) -> Dict:
    """Delete a specific collection by name - core function"""
    user_attr, _ = get_user_attribute(session, user_id)
    if not get_collection(user_attr, collection_name):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Collection {collection_name} not found"
        )
    
    # Delete the collection and commit changes
    # Create a copy of the collections dictionary
    collections_copy = dict(user_attr.collections)
    
    # Remove the collection from the copy
    collections_copy.pop(collection_name, None)
    
    # Assign the modified copy back to the model
    user_attr.collections = collections_copy
    
    session.add(user_attr)
    session.commit()
    session.refresh(user_attr)
    
    return user_attr.collections

async def delete_user_collection(
    collection_name: str,
    current_user: User = Depends(get_local_user)
) -> CollectionResponse:
    """Delete a specific collection by name - API endpoint"""
    with rx.session() as session:
        collections = delete_user_collection_core(session, current_user.id, collection_name)
        return CollectionResponse(collections=collections)


def add_collection_entry_core(session: Session, user_id: int, collection_name: str, entry: Dict[str, Any]) -> Dict:
    """Add an entry to a specific collection - core function"""
    user_attr = session.exec(
        select(UserAttribute).where(UserAttribute.user_id == user_id)
    ).first()
    
    if not user_attr or collection_name not in user_attr.collections:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Collection {collection_name} not found"
        )
    
    # Get the collection and add the new entry
    collection = user_attr.collections[collection_name]
    if not isinstance(collection, dict):
        collection = {}
        
    collection[entry['entry_id']] = entry['data']
    user_attr.collections[collection_name] = collection
    
    session.commit()
    session.refresh(user_attr)
    
    return user_attr.collections


async def add_collection_entry(
    collection_name: str,
    entry: Dict[str, Any],
    current_user: User = Depends(get_local_user)
) -> CollectionResponse:
    """Add an entry to a specific collection - API endpoint"""
    with rx.session() as session:
        collections = add_collection_entry_core(session, current_user.id, collection_name, entry)
        return CollectionResponse(collections=collections)


def setup_api(app: rx.App) -> None:
    """Initialize collection-related API routes"""
    app.api.add_api_route(
        "/api/collections",
        get_user_collections,
        methods=["GET"],
        response_model=CollectionResponse
    )
    app.api.add_api_route(
        "/api/collections",
        add_user_collection,
        methods=["POST"],
        response_model=CollectionResponse
    )
    app.api.add_api_route(
        "/api/collections/{collection_name}",
        delete_user_collection,
        methods=["DELETE"],
        response_model=CollectionResponse
    )
    app.api.add_api_route(
        "/api/collections/{collection_name}/entries",
        add_collection_entry,
        methods=["POST"],
        response_model=CollectionResponse
    )
