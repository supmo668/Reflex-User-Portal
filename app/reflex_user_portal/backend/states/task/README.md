# Tasks API Documentation

## Overview

The Tasks API provides endpoints for managing and monitoring long-running tasks in the SpyGlass platform. Tasks can be accessed through two methods:

1. **State Events** - Traditional Reflex event system (requires client token)
2. **Direct Access** - Direct API access to static methods (no client token required)

## API Documentation

Full API documentation is available at `<backend_url>/docs` when running the server.

## Authentication & Task Tracking

### CLIENT_TOKEN (for State Events method)

- Required for all state event API calls
- Obtain from the admin dashboard at `/admins/tasks/` on the frontend client or by visiting the admin portal at `/admin/task/` if you have access, or by requesting from your system administrator
- One token applies to all tasks for a given client

## Task Access Methods

### 1. State Events Method (with CLIENT_TOKEN)

#### Task Progress Tracking

1. Start a task:
    To get the task_id, use the following API:
    ```bash
    POST /api/<state_name>/tasks/<client_token>/start/<task_name>
    ```

2. (WebSocket) Monitor progress:
* All tasks
    ```bash
    wscat -c /ws/<state_name>/tasks/<client_token>
    ```
* Single task
    ```bash
    wscat -c /ws/<state_name>/tasks/<client_token>/<task_id>
    ```

### 2. Direct Access Method (no CLIENT_TOKEN required)

The direct access method allows you to execute static methods decorated with `@monitored_background_task` directly through the API without going through the Reflex event system.

#### Task Progress Tracking

1. Start a task:
    ```bash
    POST /api/<state_name>/task/start/<task_name>
    ```
    Example with parameters:
    ```bash
    curl -X POST http://localhost:8000/api/example_task2/task/start/task2_with_args \
      -H "Content-Type: application/json" \
      -d '{"name": "Matt", "age": 25}'
    ```

2. Get task result:
    ```bash
    GET /api/<state_name>/task/result/<task_id>
    ```
    Example:
    ```bash
    curl http://localhost:8000/api/example_task2/task/result/fa27f2da
    ```

3. (WebSocket) Monitor progress:
    ```bash
    wscat -c ws://localhost:8000/ws/<state_name>/task/ws/<task_id>
    ```

## Implementing Tasks

### Using the `@monitored_background_task` Decorator

Tasks are implemented as methods decorated with `@monitored_background_task`. For direct access, they should be static methods.

#### Example Implementation (ExampleTaskState2)

```python
class ExampleTaskState2(MonitorState):
    # Simple task without arguments
    @staticmethod
    @monitored_background_task
    async def task1(task, **kwargs):
        """Background task that updates progress."""
        for i in range(3):
            await task.update(
                progress=(i + 1) * 33,
                status=TaskStatus.PROCESSING,
            )
            await asyncio.sleep(0.5)
        return "<Task1 Result>"
    
    # Task with input arguments
    @staticmethod
    @monitored_background_task
    async def task2_with_args(task: TaskContext, task_args: InputArgs = DEFAULT_TASK_ARGS):
        """Background task that updates progress with input arguments."""
        for i in range(10):
            await task.update(
                progress=(i + 1) * 10,
                status=TaskStatus.PROCESSING,
            )
            await asyncio.sleep(0.5)
        return f"Completed task for {task_args.name}, age {task_args.age}"
```

Where `InputArgs` is a Pydantic model:

```python
class InputArgs(BaseModel):
    """Input arguments for the task."""
    name: str
    age: int
```

### Task Names

Task names can be found in the task dashboard. Current available tasks:
- [Example Task](./example_task/README.md) - Example task
- [Example Task2](./example_task2/README.md) - Example task 2 (with args)

## Example Response

```json
{
  "task_id": "abc123",
  "status": "Processing",
  "progress": 75,
  "result": "<Task Result>",
  "timestamp": "2025-05-24T12:15:30.123456"
}
```

![Task Monitor Interface](./task_monitor.png)
