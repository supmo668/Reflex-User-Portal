# Reflex User Portal

A modern, secure, and customizable user management portal built with [Reflex](https://reflex.dev) and [Clerk](https://clerk.com) for authentication.

## Features

- 🔐 Secure authentication with Clerk
- 👥 User role management (Admin/Regular users)
- 🛡️ Route-based access control
- 📱 Responsive design with modern UI
- 🎨 Customizable theming
- 🔄 Real-time state management

## Getting Started

1. Install dependencies:
```bash
pip install reflex reflex-clerk sqlmodel
```

2. Copy `.env.template` to `.env` and configure your environment:
```bash
cp .env.template .env
```

3. Configure your environment variables in `.env`:
```bash
# APP Attributes
APP_NAME=           # Your application name
APP_ENV=DEV        # DEV or PROD

# ADMIN
ADMIN_USER_EMAILS=  # Email of the default admin user

# CLERK
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=  # Your Clerk publishable key
CLERK_SECRET_KEY=                   # Your Clerk secret key

# DB
DB_PASSWORD=       # Your database password
DB_CONN_URI=       # Production database URI (replace {YOUR-PASSWORD})
DB_LOCAL_URI=      # Local development database URI
```

4. Initialize the database:
```bash
reflex db init
```

5. Run the development server:
```bash
reflex run
```

## Key Components

### Template System (`template.py`)

The template system provides a flexible and secure way to create pages with built-in authentication and access control:

```python
@template(
    route="/admin/users",
    title="User Management",
    requires_auth=True,
    requires_admin=True
)
def user_management_page():
    return rx.vstack(...)
```

#### Features:

- **Route-based Authentication**: Automatically handles auth requirements based on route configuration
- **Role-based Access Control**: Built-in admin access checks
- **Consistent Layout**: Shared navbar and sidebar across pages
- **Theme Support**: Customizable theming with ThemeState
- **Flexible Content**: Supports any Reflex component as page content

### User State Management (`user_state.py`)

Centralized user state management with Clerk integration:

```python
class UserState(rx.State):
    """Handles user authentication and state."""
    
    @rx.var
    def is_authenticated(self) -> bool:
        return rx.cond(clerk.ClerkState.is_signed_in, True, False)

    @rx.var
    def is_admin(self) -> bool:
        return rx.cond(clerk.ClerkState.user.user_type == UserType.ADMIN, True, False)
```

#### Features:

- **Authentication State**: Real-time tracking of user authentication status
- **Role Management**: Built-in admin role support
- **User Synchronization**: Automatic sync between Clerk and local database
- **Access Control**: Helper methods for checking user permissions

## Configuration

### Environment Variables

The application uses a `.env` file for configuration. Copy `.env.template` to get started:

#### App Configuration
- `APP_NAME`: Your application name
- `APP_ENV`: Environment (DEV/PROD)
- `ADMIN_USER_EMAILS`: Email addresses for the default admin users

#### Authentication
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`: Your Clerk publishable key
- `CLERK_SECRET_KEY`: Your Clerk secret key

#### Database
- `DB_PASSWORD`: Database password
- `DB_CONN_URI`: Production database connection string
- `DB_LOCAL_URI`: Local development database URI (defaults to SQLite)

### Template Configuration (`template_config.py`)

Define route requirements and navigation structure:

```python
NAV_ITEMS = [
    NavItem(
        name="Dashboard",
        route="/dashboard",
        requires_auth=True,
        admin_only=False
    ),
    NavItem(
        name="User Management",
        route="/admin/users",
        requires_auth=True,
        admin_only=True
    )
]
```

## Customization

### Adding New Pages

1. Create a new page in the `pages` directory
2. Use the `@template` decorator with appropriate auth requirements
3. Add the route to `NAV_ITEMS` in `template_config.py`

### Modifying User Roles

1. Update `UserType` enum in `models/user.py`
2. Add corresponding checks in `UserState`
3. Update route requirements in `template_config.py`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this in your own projects!
