#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_FILE="$SCRIPT_DIR/task_status.json"

HOST_URL=${HOST_URL:-http://localhost:8002}
CLIENT_TOKEN=${CLIENT_TOKEN:-eef4ba96-0cc0-4a83-c977-b86ace87dbfe}

# If TASK_ID is provided, get specific task results, otherwise get all tasks
if [ -n "$TASK_ID" ]; then
    echo "Getting results for task: $TASK_ID"
    curl -X GET "$HOST_URL/api/example_task2/tasks/$CLIENT_TOKEN/$TASK_ID" -o "$OUTPUT_FILE"
else
    echo "Getting results for all tasks..."
    curl -X GET "$HOST_URL/api/example_task2/tasks/$CLIENT_TOKEN" -o "$OUTPUT_FILE"
fi

echo "Results saved to $OUTPUT_FILE"
cat "$OUTPUT_FILE"