#!/usr/bin/env python
"""
Comprehensive test script for the task execution system.
This script tests:
1. Starting a task via the direct API
2. Monitoring task progress via WebSocket
3. Retrieving the final task result
"""

import asyncio
import websockets
import json
import sys
import argparse
import logging
import requests
import time
from urllib.parse import quote

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TaskTester:
    """Class to test the task execution system."""
    
    def __init__(self, base_url="http://localhost:8000", state_name="example_task2"):
        self.base_url = base_url
        self.state_name = state_name
        self.api_base = f"{base_url}/api/{state_name}"
        self.ws_base = f"ws://localhost:8000/ws/{state_name}"
        
    async def start_task(self, task_name, params=None):
        """Start a task and return the task ID."""
        url = f"{self.api_base}/task/start/{task_name}"
        logger.info(f"Starting task {task_name} at {url}")
        
        try:
            response = requests.post(url, json=params)
            response.raise_for_status()
            data = response.json()
            task_id = data.get("task_id")
            logger.info(f"Task started with ID: {task_id}")
            return task_id
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            logger.error(f"Response: {e.response.text}")
        except Exception as e:
            logger.error(f"Error starting task: {str(e)}")
        
        return None
    
    async def monitor_task(self, task_id, timeout=30):
        """Monitor task progress via WebSocket."""
        # The correct WebSocket endpoint based on the API_ROUTES in commands.py
        uri = f"{self.ws_base}/task/ws/{task_id}"
        logger.info(f"Monitoring task progress at {uri}")
        
        start_time = time.time()
        history = []
        final_status = None
        
        try:
            async with websockets.connect(uri) as websocket:
                logger.info("Connected to WebSocket")
                
                while time.time() - start_time < timeout:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        data = json.loads(message)
                        
                        # Store all messages in history
                        history.append(data)
                        
                        # Process based on message type
                        if data.get("type") == "history":
                            logger.info(f"Received task history with {len(data.get('data', {}).get('history', []))} entries")
                        
                        elif data.get("type") == "new_history":
                            logger.info(f"Received {len(data.get('data', {}).get('new_entries', []))} new history entries")
                        
                        elif data.get("type") == "status_update":
                            status_data = data.get("data", {})
                            status = status_data.get("status")
                            progress = status_data.get("progress")
                            timestamp = status_data.get("timestamp")
                            
                            logger.info(f"Task status: {status}, Progress: {progress}%, Time: {timestamp}")
                            
                            # Check if task is completed or errored
                            if status in ["Completed", "Error", "NOT_FOUND"]:
                                logger.info(f"Task {status.lower()}, closing connection")
                                final_status = status
                                break
                        
                        else:
                            logger.info(f"Received message: {json.dumps(data, indent=2)}")
                    
                    except asyncio.TimeoutError:
                        # This is fine, just continue waiting
                        continue
                
                # If we've been monitoring for too long without completion
                if final_status is None:
                    logger.warning(f"Monitoring timed out after {timeout} seconds")
        
        except websockets.exceptions.ConnectionClosed:
            logger.error("WebSocket connection closed unexpectedly")
        except Exception as e:
            logger.error(f"Error in WebSocket connection: {str(e)}")
        
        return final_status, history
    
    async def get_task_result(self, task_id):
        """Get the final task result."""
        url = f"{self.api_base}/task/result/{task_id}"
        logger.info(f"Getting task result from {url}")
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Task result: {json.dumps(data, indent=2)}")
            return data
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            logger.error(f"Response: {e.response.text}")
        except Exception as e:
            logger.error(f"Error getting task result: {str(e)}")
        
        return None
    
    async def run_complete_test(self, task_name="task1", params=None):
        """Run a complete test of the task execution system."""
        logger.info(f"=== Starting complete test for task '{task_name}' ===")
        
        # Step 1: Start the task
        task_id = await self.start_task(task_name, params)
        if not task_id:
            logger.error("❌ Test failed: Could not start task")
            return False
        
        logger.info(f"✓ Successfully started task with ID: {task_id}")
        
        # Step 2: Monitor task progress
        status, history = await self.monitor_task(task_id)
        if not status or status != "Completed":
            logger.error(f"❌ Test failed: Task did not complete successfully (status: {status})")
            return False
        
        logger.info(f"✓ Successfully monitored task progress (received {len(history)} updates)")
        
        # Step 3: Get the final result
        result = await self.get_task_result(task_id)
        if not result:
            logger.error("❌ Test failed: Could not retrieve task result")
            return False
        
        logger.info(f"✓ Successfully retrieved task result: {json.dumps(result, indent=2)}")
        logger.info("=== Complete test passed successfully! ===")
        return True

async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Test the task execution system")
    parser.add_argument("--task", default="task1", help="Task name to execute")
    parser.add_argument("--state", default="example_task2", help="State name")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL")
    parser.add_argument("--mode", choices=["start", "monitor", "result", "complete"], 
                      default="complete", help="Test mode")
    parser.add_argument("--task-id", help="Task ID (required for monitor and result modes)")
    args = parser.parse_args()
    
    tester = TaskTester(args.url, args.state)
    
    if args.mode == "start":
        await tester.start_task(args.task)
    elif args.mode == "monitor":
        if not args.task_id:
            logger.error("Task ID is required for monitor mode")
            return
        await tester.monitor_task(args.task_id)
    elif args.mode == "result":
        if not args.task_id:
            logger.error("Task ID is required for result mode")
            return
        await tester.get_task_result(args.task_id)
    else:  # complete
        await tester.run_complete_test(args.task)

if __name__ == "__main__":
    asyncio.run(main())
