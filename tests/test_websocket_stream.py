#!/usr/bin/env python
"""
Test script for the WebSocket streaming of task progress updates.
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

async def connect_and_stream(task_id):
    """Connect to the WebSocket endpoint and stream task status updates."""
    # The WebSocket endpoint is registered with the 'direct_ws' route which is '/task/ws/{task_id}'
    uri = f"ws://localhost:8000/ws/example_task2/task/ws/{task_id}"
    logger.info(f"Connecting to WebSocket at {uri}")
    
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
                    if status in ["Completed", "Error", "NOT_FOUND"]:
                        logger.info(f"Task {status.lower()}, closing connection")
                        break
    except websockets.exceptions.ConnectionClosed:
        logger.error("WebSocket connection closed unexpectedly")
    except Exception as e:
        logger.error(f"Error in WebSocket connection: {str(e)}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Test WebSocket streaming of task progress")
    parser.add_argument("task_id", help="Task ID to stream progress for")
    args = parser.parse_args()
    
    # Run the async function
    asyncio.run(connect_and_stream(args.task_id))

if __name__ == "__main__":
    main()
