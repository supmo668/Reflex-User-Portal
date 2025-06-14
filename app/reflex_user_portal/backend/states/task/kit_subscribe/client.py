
"""
ConvertKit API V4 Integration for SynHealth Waitlist
Simplified implementation with OAuth and modern API endpoints
"""

import requests
import json
from typing import Dict, List, Optional
from datetime import datetime
import reflex as rx

class ConvertKitV4Client:
    """ConvertKit API V4 client - simplified for waitlist"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://api.convertkit.com/v4"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def add_subscriber_to_waitlist(
        self,
        email: str,
        first_name: Optional[str] = None,
        why_interested: str = "",
        biggest_health_challenge: str = ""
    ) -> Dict:
        """Add subscriber with minimal survey data"""
        
        # Create or update subscriber
        subscriber_data = {
            "email_address": email,
            "first_name": first_name or "",
            "subscriber_state": "active",
            "fields": {
                "why_interested": why_interested,
                "biggest_health_challenge": biggest_health_challenge,
                "signup_date": datetime.now().isoformat(),
                "source": "waitlist_form"
            }
        }
        
        response = requests.post(
            f"{self.base_url}/subscribers",
            headers=self.headers,
            json=subscriber_data
        )
        
        if response.status_code == 201:
            subscriber = response.json()
            subscriber_id = subscriber["id"]
            
            # Add waitlist tag
            self._add_tag_to_subscriber(subscriber_id, "synhealth_waitlist")
            
            # Add interest-based tags
            if "sleep" in biggest_health_challenge.lower():
                self._add_tag_to_subscriber(subscriber_id, "interest_sleep")
            elif "energy" in biggest_health_challenge.lower():
                self._add_tag_to_subscriber(subscriber_id, "interest_energy")
            elif "stress" in biggest_health_challenge.lower():
                self._add_tag_to_subscriber(subscriber_id, "interest_stress")
                
            return subscriber
        else:
            response.raise_for_status()
    
    def _add_tag_to_subscriber(self, subscriber_id: str, tag_name: str):
        """Add a tag to subscriber"""
        # In V4, tags are applied differently
        tag_data = {
            "tag": {
                "name": tag_name
            }
        }
        
        requests.post(
            f"{self.base_url}/subscribers/{subscriber_id}/tags",
            headers=self.headers,
            json=tag_data
        )