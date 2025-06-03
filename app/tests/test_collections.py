"""Tests for collection management functionality"""
import pytest
import reflex as rx
from datetime import datetime, timezone
from sqlmodel import select
from fastapi import HTTPException

from reflex_user_portal.models import UserAttribute, User, UserType
from reflex_user_portal.backend.api.user import (
    get_user_attribute,
    get_collection,
    get_user_collections_core,
    add_user_collection_core,
    delete_user_collection_core
)


@pytest.fixture
def test_session():
    """Create a test session"""
    with rx.session() as session:
        yield session

@pytest.fixture
def test_user(test_session):
    """Get or create a test user for testing"""
    # Try to find existing test user
    user = test_session.exec(
        select(User).where(User.email == "test@default.com")
    ).first()
    
    if not user:
        # Create new test user if not found
        user = User(
            email="test@default.com",
            clerk_id="test_clerk_id",
            user_type=UserType.USER.value,
            first_name="Test",
            last_name="User",
            created_at=datetime.now(timezone.utc)
        )
        test_session.add(user)
        test_session.commit()
        test_session.refresh(user)
    
    return user


class TestUserAttribute:
    """Tests for user attribute functionality"""
    
    def test_get_user_attribute_lifecycle(self, test_session, test_user):
        """Test the complete lifecycle of user attributes"""
        # Clean up any existing user attribute
        existing = test_session.exec(
            select(UserAttribute).where(UserAttribute.user_id == test_user.id)
        ).first()
        if existing:
            test_session.delete(existing)
            test_session.commit()
        
        # Test creating new attribute
        user_attr, created = get_user_attribute(test_session, test_user.id)
        assert created is True
        assert user_attr is not None
        assert user_attr.user_id == test_user.id
        assert user_attr.collections == {}
        
        # Test getting existing attribute
        found_attr, created = get_user_attribute(test_session, test_user.id)
        assert created is False
        assert found_attr.user_id == user_attr.user_id
        assert found_attr.collections == user_attr.collections
    
    def test_get_user_attribute_invalid_user(self, test_session):
        """Test error handling for invalid user"""
        with pytest.raises(HTTPException) as exc:
            get_user_attribute(test_session, 999)
        assert exc.value.detail == "User not found"


class TestCollections:
    """Tests for collection management functionality"""
    
    def test_collection_lifecycle(self, test_session, test_user):
        """Test the complete lifecycle of collections"""
        # Clean up any existing user attribute
        existing = test_session.exec(
            select(UserAttribute).where(UserAttribute.user_id == test_user.id)
        ).first()
        if existing:
            test_session.delete(existing)
            test_session.commit()
        
        # Create a new user attribute
        user_attr, _ = get_user_attribute(test_session, test_user.id)
        
        # Create collection
        test_collection_data = {
            "description": "Test collection",
            "entries": {}
        }
        collections = add_user_collection_core(test_session, test_user.id, "test_collection", test_collection_data)
        assert "test_collection" in collections
        assert collections["test_collection"]["description"] == "Test collection"
        
        # Read collection (both specific and all)
        collection = get_collection(user_attr, "test_collection")
        assert collection is not None
        assert collection["description"] == "Test collection"
        
        collections = get_user_collections_core(test_session, test_user.id)
        assert "test_collection" in collections
        
        # Test non-existent collection
        assert get_collection(user_attr, "nonexistent") is None
        
        # Delete collection
        collections = delete_user_collection_core(test_session, test_user.id, "test_collection")
        assert "test_collection" not in collections
        assert get_collection(user_attr, "test_collection") is None
