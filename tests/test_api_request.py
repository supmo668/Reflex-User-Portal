#!/usr/bin/env python
"""
Test script to perform direct task execution API requests.
"""

import asyncio
import aiohttp
import sys
import os
import argparse
import json

async def test_direct_task_execution(task_name="task1", params=None):
    """Test the direct task execution API endpoint."""
    print(f"Testing direct task execution for task: {task_name}")
    
    # Construct the API URL
    base_url = "http://localhost:8000/api/example_task2/task"
    url = f"{base_url}/direct_start/{task_name}"
    
    # Make the API request
    async with aiohttp.ClientSession() as session:
        try:
            print(f"Making POST request to: {url}")
            if params:
                async with session.post(url, json=params) as response:
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
                        # Wait a moment for the task to start
                        await asyncio.sleep(2)
                        
                        # Check task status
                        status_url = f"{base_url}/direct_result?task_id={task_id}"
                        print(f"Checking task status at: {status_url}")
                        
                        async with session.get(status_url) as status_response:
                            status_text = await status_response.text()
                            print(f"Status response: {status_text}")
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
    
    await test_direct_task_execution(args.task, params)

if __name__ == "__main__":
    asyncio.run(main())
