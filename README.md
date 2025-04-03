# Reflex User Portal

A modern, secure, and customizable user management portal built with [Reflex](https://reflex.dev) and [Clerk](https://clerk.com) for authentication.

## Environment Setup

### Required Environment Variables
```bash
# Application Configuration
APP_NAME=           # Your application name
APP_ENV=DEV        # DEV or PROD
ADMIN_USER_EMAILS=  # Comma-separated list of admin emails

# Authentication (Clerk)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=  # Your Clerk publishable key
CLERK_SECRET_KEY=                   # Your Clerk secret key

# Database Configuration
DB_PASSWORD=       # Database password
DB_CONN_URI=       # Production database URI (format: postgresql://user:pass@host:port/db)
DB_LOCAL_URI=      # Local development database URI
```

### Quick Start

1. Install dependencies:
```bash
pip install reflex reflex-clerk sqlmodel
```

2. Set up environment:
```bash
cp .env.template .env
# Edit .env with your configuration
```

3. Initialize and run:
```bash
reflex db init
reflex run
```

## Core Technical Components

### 1. User Management & Authentication

#### User Types Configuration
Location: `models/user.py`
```python
class UserType(str, Enum):
    ADMIN = "admin"
    USER = "user"
    # Add custom user types here
```

#### Role Management
- Define roles in `models/user.py`
- Implement checks in `UserAuthState`
- Configure access in `template_config.py`

### 2. Custom API & Admin Configuration

#### Model Definition
Location: `models/admin_config.py`
```python
class CustomConfig(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    configuration: Dict[str, Any] = Field(default={})
```

Register in MODEL_FACTORY:
```python
MODEL_FACTORY = {
    "admin_config": AdminConfig,
    "custom_config": CustomConfig
}
```

#### API Integration
1. Add routes in `backend/api/`
2. Link configurations in `backend/custom_api_state.py`
3. Access via `/admin/settings`

### Core Features

- 🔐 Secure Clerk authentication
- 👥 User role management
- 🛡️ Route-based access control
- 📱 Responsive design
- 🎨 Customizable theming
- 🔄 Real-time state management

---

## Technical Development Guide

### Project Architecture

#### 1. Authentication System
The authentication system uses Clerk with these key files:
- `backend/user.py`: Auth state management
- `templates/template.py`: Route protection
- `models/user.py`: User types and roles

Protected Routes Example:
```python
@template(
    route="/protected/route",
    requires_auth=True,
    requires_admin=False
)
def protected_page():
    return rx.vstack(...)
```

**Role Management**
- Define roles in `models/user.py`
- Implement role checks in `UserAuthState`
- Configure access in `template_config.py`

#### 2. Navigation System

The navigation structure is configured in `template_config.py`:
```python
NAV_ITEMS = [
    NavItem(
        name="Dashboard",
        route="/dashboard",
        requires_auth=True,
        admin_only=False
    )
]
```

#### 3. Template System Architecture (`template.py`)
The template system provides:
- Route-based authentication controls
- Role-based access management
- Consistent layout structure
- Theme configuration support

#### 4. State Management

**UserAuthState** (`user.py`):
- Handles route protection logic
- Manages data synchronization
- Controls role-based permissions
- Implements smart redirection

**Custom API State** (`backend/custom_api_state.py`):
- Links DB configurations to workloads
- Manages custom API integrations
- Handles state persistence

#### 5. Admin Configuration System

**Model Definition** (`models/admin_config.py`):
- Define custom models for admin configuration
- Register models in MODEL_FACTORY
- Configure database schemas

**API Integration**:
- Custom routes in `backend/api/`
- State management in `backend/custom_api_state.py`
- Admin dashboard at `/admin/settings`

### Development Guidelines

1. **Adding New Features**
   - Place API routes in `backend/api/`
   - Add corresponding states in `backend/custom_api_state.py`
   - Update MODEL_FACTORY if new models are needed

2. **Extending Admin Configuration**
   - Define new models in `models/admin_config.py`
   - Register in MODEL_FACTORY
   - Add corresponding API endpoints

3. **Custom Workload Integration**
   - Add routes in `backend/api/`
   - Create state handlers in `backend/custom_api_state.py`
   - Link configurations from DB to workload

## Backend API Documentation

### Background Tasks API

The backend provides REST APIs and WebSocket endpoints for managing long-running background tasks.

#### 1. Starting a Task

Tasks can be started via POST request. Tasks requiring parameters must provide them in the request body according to their Pydantic model definition.

**Endpoint Structure:**
```
POST /api/{state_name}/tasks/{client_token}/start/{task_name}
```

**Example - Starting a task with parameters:**
```bash
# Task with InputArgs model parameters
curl -X POST \
  -H "Content-Type: application/json" \
  http://localhost:8000/api/example_task2/tasks/{client_token}/start/loaded_task \
  -d '{"name": "bob", "age": 6}'
```

The parameter structure is defined by Pydantic models:
```python
# model.py
class InputArgs(BaseModel):
    name: str
    age: int
```

#### 2. Monitoring Tasks

##### REST Endpoints

Get task status:
```bash
# Get specific task
GET /api/{state_name}/tasks/{client_token}/status/{task_id}

# Get all tasks
GET /api/{state_name}/tasks/{client_token}/status
```

Get task result:
```bash
GET /api/{state_name}/tasks/{client_token}/result/{task_id}
```

##### WebSocket Monitoring

Connect to WebSocket for real-time updates:
```bash
# Monitor specific task
ws://localhost:8000/api/tasks/{client_token}/{task_id}/monitor

# Monitor all tasks
ws://localhost:8000/api/tasks/{client_token}/monitor
```

WebSocket messages follow this structure:
```json
{
    "type": "state_update",
    "data": {
        "task_id": "xxx",
        "status": "PROCESSING|COMPLETED|ERROR",
        "progress": 0-100,
        "result": "task result when completed",
        "error": "error message if failed"
    }
}
```

Example WebSocket client:
```python
import websockets
import asyncio
import json

async def monitor_task(client_token, task_id=None):
    url = f"ws://localhost:8000/ws/example_task2/tasks/{client_token}"
    if task_id:
        url = f"{url}/{task_id}"
        
    async with websockets.connect(url) as ws:
        while True:
            msg = await ws.recv()
            state = json.loads(msg)
            print(f"Task update: {state}")
            
            if state["data"]["status"] in ["COMPLETED", "ERROR"]:
                break

# Usage
asyncio.run(monitor_task("your-client-token", "task-id"))
```

### Development Guidelines

1. **Adding New Task Types**
   - Define task logic in state classes using `@monitored_background_task` decorator
   - For tasks with parameters:
     - Create Pydantic models in `model.py`
     - Use `task_args` as the parameter name in your function signature
     - Example:
       ```python
       @monitored_background_task
       async def my_task(self, task: TaskContext, task_args: MyInputModel):
           """Task description here."""
           # task_args will be automatically validated against MyInputModel
           result = await process(task_args.field1, task_args.field2)
           return result
       ```
   - Task methods should use `TaskContext` for progress updates

2. **Task Status Updates**
   - Use `task.update()` for progress and status changes
   - Status values: PROCESSING, COMPLETED, ERROR
   - Include progress (0-100) for long-running tasks

3. **Error Handling**
   - Tasks should handle exceptions and update status accordingly
   - Use `TaskError` for specific task failures
   - WebSocket connections handle disconnects gracefully

## Contributing

Contributions welcome! Please submit Pull Requests.

## License

MIT License
