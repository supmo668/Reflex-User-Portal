"""
ConvertKit v4 API email subscription onboarding state.

This state handles email subscription workflows for onboarding users
to email lists using the ConvertKit v4 API.
"""
import os
from datetime import datetime
import reflex as rx
import requests
from typing import Dict, Any

from app.reflex_user_portal.utils.logger import get_logger
from app.config import CONVERTKIT_API_KEY, CONVERTKIT_API_BASE, APP_DISPLAY_NAME

logger = get_logger(__name__)

class OnboardingTaskState(rx.State):
    """State for handling ConvertKit email subscription onboarding.
    
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
        """Subscribe user to ConvertKit waitlist."""
        self.is_subscribing = True
        yield  # Send loading state to frontend
        
        logger.info(f"Starting waitlist subscription for {self.email}")
        
        try:
            # Call ConvertKit v4 API directly
            result = self._call_convertkit_v4_api()
            
            # Update UI state
            self.subscription_status = "success"
            self.subscription_message = "Successfully subscribed to waitlist!"
            
            logger.info(f"Successfully subscribed {self.email} to waitlist")
            
        except Exception as e:
            logger.error(f"Error subscribing to waitlist: {str(e)}")
            self.subscription_status = "error"
            self.subscription_message = f"Subscription failed: {str(e)}"
        
        finally:
            self.is_subscribing = False
    
    def _call_convertkit_v4_api(self) -> Dict[str, Any]:
        """Call the ConvertKit v4 API to subscribe the user."""
        
        if not CONVERTKIT_API_KEY:
            raise ValueError("CONVERTKIT_API_KEY environment variable is required")
        
        # Prepare request payload for ConvertKit v4
        payload = {
            "email_address": self.email,
            "state": "active",
            "fields": {
                "Source": self.signup_source,
                "Signup Date": datetime.now().strftime("%Y-%m-%d")
            }
        }
        
        # Prepare headers for ConvertKit v4
        headers = {
            "X-Kit-Api-Key": CONVERTKIT_API_KEY,
            "Content-Type": "application/json"
        }
        
        # Make API request to ConvertKit v4 subscribers endpoint
        url = f"{CONVERTKIT_API_BASE}/subscribers"
        
        logger.info(f"Calling ConvertKit v4 API: {url}")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code not in [200, 201]:
            error_msg = f"ConvertKit v4 API error: {response.status_code} - {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        result = response.json()
        logger.info(f"ConvertKit v4 API response: {result}")
        
        return result
