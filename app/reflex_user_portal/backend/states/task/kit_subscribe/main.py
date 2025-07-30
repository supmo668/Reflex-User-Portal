"""
Brevo API email subscription onboarding state.

This state handles email subscription workflows for onboarding users
to email lists using the Brevo API (formerly Sendinblue).
Note: This is a mocked implementation for development purposes.
"""
import os
from datetime import datetime
import reflex as rx
import time
from typing import Dict, Any

from app.utils.logger import get_logger
from app.config import APP_DISPLAY_NAME

# Brevo API configuration (mocked for development)
BREVO_API_KEY = os.getenv("BREVO_API_KEY", "mock_brevo_key")
BREVO_API_BASE = "https://api.brevo.com/v3"
BREVO_LIST_ID = os.getenv("BREVO_LIST_ID", "1")  # Default list ID

logger = get_logger(__name__)

class OnboardingTaskState(rx.State):
    """State for handling Brevo email subscription onboarding.
    
    This state provides a minimalist email subscription workflow.
    """
    
    # Form fields for the onboarding UI
    email: str = ""
    signup_source: str = APP_DISPLAY_NAME
    
    # Loading state
    is_subscribing: bool = False
    
    # Subscription status
    subscription_status: str = ""
    subscription_message: str = ""
    
    def set_email(self, email: str):
        """Set the email field."""
        self.email = email
        # Clear previous status when user starts typing
        if self.subscription_status:
            self.subscription_status = ""
            self.subscription_message = ""
    
    def clear_form(self):
        """Clear all form fields."""
        self.email = ""
        self.subscription_status = ""
        self.subscription_message = ""
        self.is_subscribing = False
    
    @rx.event
    def subscribe_to_waitlist(self):
        """Subscribe user to Brevo waitlist (mocked for development)."""
        self.is_subscribing = True
        yield  # Send loading state to frontend
        
        logger.info(f"Starting Brevo waitlist subscription for {self.email}")
        
        try:
            # Call mocked Brevo API
            result = self._call_brevo_api_mock()
            
            # Update UI state
            self.subscription_status = "success"
            self.subscription_message = "Successfully subscribed to waitlist!"
            
            logger.info(f"Successfully subscribed {self.email} to Brevo waitlist (mocked)")
            
        except Exception as e:
            logger.error(f"Error subscribing to Brevo waitlist: {str(e)}")
            self.subscription_status = "error"
            self.subscription_message = f"Subscription failed: {str(e)}"
        
        finally:
            self.is_subscribing = False
    
    def _call_brevo_api_mock(self) -> Dict[str, Any]:
        """Mock Brevo API call to simulate email subscription (no real API call)."""
        
        # Simulate API processing time
        time.sleep(1)  # Mock API delay
        
        # Validate email format (basic validation)
        if not self.email or "@" not in self.email:
            raise ValueError("Invalid email address format")
        
        # Prepare mock payload that would be sent to Brevo API
        mock_payload = {
            "email": self.email,
            "listIds": [int(BREVO_LIST_ID)],
            "attributes": {
                "SOURCE": self.signup_source,
                "SIGNUP_DATE": datetime.now().strftime("%Y-%m-%d"),
                "SIGNUP_TIME": datetime.now().strftime("%H:%M:%S")
            },
            "updateEnabled": True
        }
        
        # Mock headers that would be used
        mock_headers = {
            "api-key": BREVO_API_KEY,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Mock API endpoint
        mock_url = f"{BREVO_API_BASE}/contacts"
        
        logger.info(f"[MOCKED] Brevo API call to: {mock_url}")
        logger.info(f"[MOCKED] Payload: {mock_payload}")
        
        # Simulate successful response
        mock_response = {
            "id": f"mock_contact_{hash(self.email) % 10000}",
            "email": self.email,
            "listIds": [int(BREVO_LIST_ID)],
            "attributes": mock_payload["attributes"],
            "createdAt": datetime.now().isoformat(),
            "modifiedAt": datetime.now().isoformat()
        }
        
        logger.info(f"[MOCKED] Brevo API response: {mock_response}")
        
        return mock_response
