#!/usr/bin/env python
"""
Test script for WebSocket streaming of task status updates.
This script will:
1. Get a task ID from the command line (from a previously started task)
2. Connect to the WebSocket endpoint to stream updates
"""

import asyncio
import websockets
import json
import sys
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def monitor_task_progress(task_id, state_name="example_task2"):
    """Monitor task progress via WebSocket for an existing task."""
    # The WebSocket endpoint is registered with the 'direct_ws' route
    uri = f"ws://localhost:8000/ws/{state_name}/task/{task_id}"
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

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Test WebSocket streaming of task status")
    parser.add_argument("task_id", help="Task ID to monitor")
    parser.add_argument("--state", default="example_task2", help="State name (default: example_task2)")
    args = parser.parse_args()
    
    # Run the async function
    asyncio.run(monitor_task_progress(args.task_id, args.state))

if __name__ == "__main__":
    main()
