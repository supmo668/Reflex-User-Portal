#!/bin/bash

# Test script for example_task2 API endpoints
# This script first gets a client token, then tests the task2_with_args API endpoint

# Base URL
BASE_URL="http://localhost:8000"

# Step 1: Get a client token
echo "Step 1: Getting a client token..."
TOKEN_RESPONSE=$(curl -s -X GET "${BASE_URL}/api/example_task2/client/token")

# Extract the client token using grep and cut
CLIENT_TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"client_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$CLIENT_TOKEN" ]; then
    echo "Failed to get client token. Response was: $TOKEN_RESPONSE"
    # Fallback to a default token if provided as argument
    CLIENT_TOKEN=${1:-"test-client-token"}
    echo "Using fallback client token: $CLIENT_TOKEN"
else
    echo "Successfully obtained client token: $CLIENT_TOKEN"
fi

# Step 2: Test the task API
echo -e "\nStep 2: Testing task2_with_args API endpoint..."

# API endpoint for task
TASK_API_URL="${BASE_URL}/api/example_task2/tasks/${CLIENT_TOKEN}/start/task2_with_args"

# Request body based on InputArgs model
REQUEST_BODY='{
  "name": "TestUser",
  "age": 30
}'

echo "Sending request to: ${TASK_API_URL}"
echo "Request body: ${REQUEST_BODY}"

# Send the request
TASK_RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d "${REQUEST_BODY}" \
  "${TASK_API_URL}")

echo -e "\nTask API Response: $TASK_RESPONSE"

# Extract task ID
TASK_ID=$(echo $TASK_RESPONSE | grep -o '"task_id":"[^"]*"' | cut -d'"' -f4)

if [ -n "$TASK_ID" ]; then
    echo -e "\nTask ID: $TASK_ID"
    
    # Check task status
    echo -e "\nChecking task status..."
    STATUS_URL="${BASE_URL}/api/example_task2/tasks/${CLIENT_TOKEN}/status/${TASK_ID}"
    curl -s -X GET "${STATUS_URL}"
    
    echo -e "\n\nTo check task status again, use:"
    echo "curl -X GET ${STATUS_URL}"
else
    echo -e "\nFailed to get task ID. Response was: $TASK_RESPONSE"
fi
