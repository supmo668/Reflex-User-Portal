#!/usr/bin/env python
"""
Test script for the direct task execution API with the correct URL structure.
"""

import asyncio
import aiohttp
import sys
import os
import json
import argparse

async def test_direct_task_api(task_name="task1", parameters=None):
    """Test the direct task execution API with the correct URL structure."""
    print(f"Testing direct task execution API for task: {task_name}")
    
    # Construct the API URL based on the API_ROUTES in commands.py
    base_url = "http://localhost:8000/api/example_task2"
    url = f"{base_url}/task/start/{task_name}"
    
    print(f"Making POST request to: {url}")
    
    # Make the API request
    async with aiohttp.ClientSession() as session:
        try:
            if parameters:
                async with session.post(url, json=parameters) as response:
                    status = response.status
                    response_text = await response.text()
            else:
                async with session.post(url) as response:
                    status = response.status
                    response_text = await response.text()
            
            print(f"Response status: {status}")
            print(f"Response body: {response_text}")
            
            # If successful, get the task ID and check status
            if status == 200:
                try:
                    response_json = json.loads(response_text)
                    task_id = response_json.get("task_id")
                    if task_id:
                        print(f"Task ID: {task_id}")
                        
                        # Poll for task status
                        for _ in range(10):  # Poll for up to 10 seconds
                            await asyncio.sleep(1)
                            
                            # Check task status with the correct URL
                            result_url = f"{base_url}/task/result/{task_id}"
                            print(f"Checking task result at: {result_url}")
                            
                            try:
                                async with session.get(result_url) as result_response:
                                    if result_response.status == 200:
                                        result_text = await result_response.text()
                                        print(f"Result response: {result_text}")
                                        return
                                    else:
                                        print(f"Result check status: {result_response.status}")
                                        print(f"Result check response: {await result_response.text()}")
                            except Exception as e:
                                print(f"Error checking result: {str(e)}")
                except json.JSONDecodeError:
                    print("Failed to parse response as JSON")
        except aiohttp.ClientError as e:
            print(f"Error making request: {str(e)}")

async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Test direct task execution API")
    parser.add_argument("--task", choices=["task1", "task2_with_args"], default="task1", 
                        help="Task to execute")
    parser.add_argument("--params", type=str, help="JSON parameters for the task")
    args = parser.parse_args()
    
    params = None
    if args.params:
        try:
            params = json.loads(args.params)
        except json.JSONDecodeError:
            print(f"Error parsing JSON parameters: {args.params}")
            return
    
    await test_direct_task_api(args.task, params)

if __name__ == "__main__":
    asyncio.run(main())
