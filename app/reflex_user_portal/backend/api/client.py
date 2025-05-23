"""
Example client API for creating and managing client tokens.

Note: This module doesn't work as Reflex doesn't support direct client tokens creation and management due to security .
"""
# Import necessary modules and classes
from fastapi import FastAPI, Body
from typing import Dict, Any, Optional
import uuid

import reflex as rx
from .commands import get_route
from ...utils.logger import get_logger
from ...utils.error_handler import create_error_response

logger = get_logger(__name__)


class ClientAPI:
    """
    Class responsible for setting up API endpoints for client token management.
    Provides endpoints to create and retrieve client tokens for state instances.
    """
    def __init__(self, app: rx.App, state_name: str, state_info: Dict[str, Any]):
        self.app = app
        self.api_base_path = state_info.get("api_prefix", "/api")
        self.state_cls = state_info["cls"]
        self.state_name = state_name
        self.setup_routes(app.api_transformer)
    
    async def create_client_token(self):
        """
        Create a new client token and initialize a state instance for the specified state type.
        
        Args:
            state_name: The name of the state to initialize (must be a key in STATE_MAPPINGS)
        
        Returns:
            A dictionary with the client token and state type information
        """
        # Generate a new client token
        client_token = str(uuid.uuid4())
        
        try:
            # manager = rx.istate.manager.StateManager.create(self.state_cls)
            # Retrieve the state instance for the token (will initialize if it doesn't exist)
            # manager.set_state(client_token, self.state_cls)
            task_method = getattr(self.state_cls, "task1", None)
            async with self.app.state_manager.modify_state(client_token) as state_manager:
                state = await state_manager.get_state(self.state_cls)
                state.reset()
                logger.debug(f"State instance: {state}")
            logger.info(f"Created new client token '{client_token}' for state type '{self.state_name}'")
                
            
            # Return the client token and state information
            return {
                "client_token": client_token,
            }
            
        except Exception as e:
            logger.error(f"Error creating client token: {str(e)}")
            return create_error_response({
                "error": "Failed to create client token",
                "message": str(e),
                "code": 500
            })
    
    def setup_routes(self, app_instance: FastAPI):
        """
        Set up API endpoints for client token management.
        """
        # Route for creating a new client token for a specific state type
        app_instance.post(
            get_route("token", self.api_base_path)
        )(self.create_client_token)
