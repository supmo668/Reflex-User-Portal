#!/usr/bin/env python
"""
Test script for the direct task result endpoint.
"""

import requests
import sys
import os
import json
import argparse

def test_direct_result(task_id):
    """Test the direct task result endpoint with the correct HTTP method and URL."""
    print(f"Testing direct task result endpoint for task ID: {task_id}")
    
    # Construct the API URL based on the API_ROUTES in commands.py
    base_url = "http://localhost:8000/api/example_task2"
    url = f"{base_url}/task/result/{task_id}"
    
    print(f"Making GET request to: {url}")
    
    # Make the API request with the correct HTTP method (GET)
    response = requests.get(url)
    
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")
    
    if response.status_code == 200:
        try:
            result = response.json()
            print(f"Task result: {result}")
        except json.JSONDecodeError:
            print("Failed to parse response as JSON")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Test direct task result endpoint")
    parser.add_argument("task_id", help="Task ID to get the result for")
    args = parser.parse_args()
    
    test_direct_result(args.task_id)

if __name__ == "__main__":
    main()
