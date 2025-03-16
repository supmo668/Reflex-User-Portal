import reflex as rx
from reflex_user_portal.models.user_attribute import UserAttribute
from typing import List 
import sqlalchemy

from reflex_user_portal.models.user_attribute import UserAttribute
from reflex_user_portal.models.user_attribute import Query

class UserDataState(rx.State):
    user_attributes: List[UserAttribute]
    
    @rx.event
    def load_user_data(self):
        """Load user attributes and related queries."""
        with rx.session() as session:
            self.user_attributes = session.exec(
                UserAttribute.select.options(
                    sqlalchemy.orm.selectinload(UserAttribute.user),
                    sqlalchemy.orm.selectinload(UserAttribute.user_queries)
                )
            ).all()
    
    @rx.event
    def get_user_queries(self, user_id: int):
        """Get queries for a specific user."""
        with rx.session() as session:
            return session.exec(
                Query.select().where(
                    Query.user_id == user_id
                )
            ).all()
            
    @rx.event
    def add_query(self, user_id: int, query_text: str):
        """Add a new query for a user."""
        with rx.session() as session:
            user_attr = session.exec(
                UserAttribute.select().where(
                    UserAttribute.user_id == user_id
                )
            ).first()
            
            new_query = Query(
                user_id=user_id,
                user_attribute_id=user_attr.id,
                query=query_text
            )
            session.add(new_query)
            session.commit()
            session.refresh(new_query)