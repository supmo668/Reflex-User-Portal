#!/usr/bin/env python
"""
Test script for the direct task execution API.

This script tests the simplified implementation of the run_task_direct method.
"""

import asyncio
import aiohttp
import sys
import os
import json
import argparse

async def test_direct_task_api(task_name="task1", parameters=None):
    """Test the direct task execution API."""
    print(f"Testing direct task execution API for task: {task_name}")
    
    # Construct the API URL
    base_url = "http://localhost:8000/api/example_task2/task"
    url = f"{base_url}/direct_start/{task_name}"
    
    # Make the API request
    async with aiohttp.ClientSession() as session:
        try:
            print(f"Making POST request to: {url}")
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
                            
                            # Check task status
                            status_url = f"{base_url}/direct_result?task_id={task_id}"
                            print(f"Checking task status at: {status_url}")
                            
                            try:
                                async with session.get(status_url) as status_response:
                                    if status_response.status == 200:
                                        status_text = await status_response.text()
                                        print(f"Status response: {status_text}")
                                        status_json = json.loads(status_text)
                                        if status_json.get("result"):
                                            print("Task completed successfully!")
                                            return
                                    else:
                                        print(f"Status check failed: {status_response.status}")
                            except Exception as e:
                                print(f"Error checking status: {str(e)}")
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
