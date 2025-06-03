#!/usr/bin/env python
"""
Test script for the complete task flow:
1. Start a task
2. Monitor its progress via WebSocket
3. Get the final result
"""

import asyncio
import websockets
import json
import sys
import argparse
import logging
import requests
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def start_task(task_name="task1", parameters=None):
    """Start a task and return the task_id."""
    url = f"http://localhost:8000/api/example_task2/task/start/{task_name}"
    logger.info(f"Starting task {task_name} at {url}")
    
    response = requests.post(url, json=parameters)
    if response.status_code == 404:
        logger.error(f"Task endpoint not found: {url}")
        return None
    
    try:
        data = response.json()
        task_id = data.get("task_id")
        logger.info(f"Task started with ID: {task_id}")
        return task_id
    except Exception as e:
        logger.error(f"Error parsing response: {str(e)}")
        logger.error(f"Response content: {response.text}")
        return None

async def monitor_task_progress(task_id):
    """Monitor task progress via WebSocket."""
    # The WebSocket endpoint is registered with the 'direct_ws' route
    uri = f"ws://localhost:8000/ws/example_task2/task/ws/{task_id}"
    logger.info(f"Monitoring task progress at {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            logger.info("Connected to WebSocket")
            
            # Keep receiving messages until the task is completed or an error occurs
            while True:
                message = await websocket.recv()
                data = json.loads(message)
                
                # Pretty print the received message
                logger.info(f"Received message: {json.dumps(data, indent=2)}")
                
                # Check if this is a status update
                if data.get("type") == "status_update":
                    status = data.get("data", {}).get("status")
                    progress = data.get("data", {}).get("progress")
                    
                    if status:
                        logger.info(f"Task status: {status}, Progress: {progress}%")
                    
                    if status in ["Completed", "Error", "NOT_FOUND"]:
                        logger.info(f"Task {status.lower()}, closing connection")
                        return status
    except websockets.exceptions.ConnectionClosed:
        logger.error("WebSocket connection closed unexpectedly")
    except Exception as e:
        logger.error(f"Error in WebSocket connection: {str(e)}")
    
    return None

async def get_task_result(task_id):
    """Get the final task result."""
    url = f"http://localhost:8000/api/example_task2/task/result/{task_id}"
    logger.info(f"Getting task result from {url}")
    
    response = requests.get(url)
    if response.status_code != 200:
        logger.error(f"Error getting task result: {response.status_code}")
        logger.error(f"Response content: {response.text}")
        return None
    
    try:
        data = response.json()
        logger.info(f"Task result: {json.dumps(data, indent=2)}")
        return data
    except Exception as e:
        logger.error(f"Error parsing result: {str(e)}")
        return None

async def run_complete_test():
    """Run the complete test flow."""
    # Step 1: Start a task
    task_id = await start_task()
    if not task_id:
        logger.error("Failed to start task")
        return
    
    # Step 2: Monitor task progress
    status = await monitor_task_progress(task_id)
    if not status or status != "Completed":
        logger.error(f"Task did not complete successfully: {status}")
        return
    
    # Step 3: Get the final result
    result = await get_task_result(task_id)
    if not result:
        logger.error("Failed to get task result")
        return
    
    logger.info("Complete test flow successful!")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Test complete task flow")
    parser.add_argument("--task-name", default="task1", help="Task name to execute")
    args = parser.parse_args()
    
    # Run the async function
    asyncio.run(run_complete_test())

if __name__ == "__main__":
    main()
