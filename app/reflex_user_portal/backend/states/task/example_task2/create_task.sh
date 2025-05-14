#!/bin/bash
# export CLIENT_TOKEN=""
HOST_URL=${HOST_URL:-http://localhost:8001}
RESPONSE=$(curl -X POST "$HOST_URL/api/example_task2/tasks/$CLIENT_TOKEN/start/task2_with_args" \
  -H "Content-Type: application/json" \
  -d '{"name": "TOM", "age": 111}')
# Extract just the task_id and save it to TASK_ID variable
TASK_ID=$(echo $RESPONSE | jq -r '.task_id')

# Print the task_id to verify
echo "Task ID: $TASK_ID"  