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

### Authentication Architecture

The authentication system is built on two main components that work together to provide comprehensive security:

#### 1. UserState (`user_state.py`)

Handles route-level authentication and user data synchronization:

```python
class UserState(rx.State):
    user_role: str = UserType.GUEST.value
    redirect_after_login: Optional[str] = None

    @rx.event
    async def sync_auth_state(self):
        # Handles authentication redirects
        # Syncs Clerk user data to internal database
        # Manages user roles and permissions
```

**Key Features:**
- **Route Protection**: Prevents unauthorized direct access to protected routes
- **Data Synchronization**: Maintains consistency between Clerk and internal user database
- **Role Management**: Handles user role assignment and verification
- **Smart Redirection**: Preserves intended destination after authentication

#### 2. Template System (`template.py`)

Manages component-level access control and user experience:

```python
@template(
    route="/admin/users",
    requires_auth=True,
    requires_admin=True
)
def protected_page():
    # Page content
```

**Key Features:**
- **Content Protection**: Shows appropriate content based on auth status
- **Graceful Fallback**: Displays profile/sign-in component for unauthorized access
- **Flexible Auth Rules**: Configurable per-route in `template_config.py`
- **Seamless UX**: Integrated auth flow with minimal redirects

#### Two-Layer Protection System

1. **Route-Level Protection** (UserState):
   ```python
   # In user_state.py
   async def sync_auth_state(self):
       if not clerk_state.is_signed_in:
           # Store intended destination
           self.redirect_after_login = self.router.page.raw_path
           # Redirect to sign-in
           return rx.redirect("/sign-in")
   ```
   - Prevents unauthorized direct URL access
   - Handles Clerk authentication state
   - Maintains user database synchronization
   - Preserves intended destination for post-login redirect

2. **Component-Level Protection** (Template):
   ```python
   # In template.py
   @template(requires_auth=True, requires_admin=True)
   def protected_page():
       return rx.cond(
           UserState.is_admin,
           page_content(),
           access_denied_page()
       )
   ```
   - Controls component visibility based on auth state
   - Shows appropriate fallback UI (profile/sign-in)
   - Manages role-based access control
   - Provides seamless user experience

3. **Integration Points**:
   - Template decorator appends `sync_auth_state` to protected routes
   - UserState maintains role information for template checks
   - Both layers use shared configuration from `template_config.py`
   - Coordinated redirection and state management

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

### Role-Based Access Control

#### Route Configuration (`template_config.py`)

Define route requirements and navigation structure:

```python
NAV_ITEMS = [
    NavItem(
        name="Dashboard",
        route="/dashboard",
        requires_auth=True,    # Requires sign-in
        admin_only=False      # Accessible to all users
    ),
    NavItem(
        name="User Management",
        route="/admin/users",
        requires_auth=True,    # Requires sign-in
        admin_only=True       # Only admins can access
    )
]
```

#### Access Control Flow

1. **Route Definition**:
   - Configure auth requirements in `NAV_ITEMS`
   - Set `requires_auth` and `admin_only` flags

2. **Authentication Check**:
   - `UserState.sync_auth_state` runs on protected routes
   - Verifies Clerk authentication status
   - Syncs user role with internal database

3. **Authorization Check**:
   - Template decorator verifies user permissions
   - Admin routes check `UserState.is_admin`
   - Shows appropriate UI based on access level

## Customization

### Authentication Flow and State Management

#### Protected Route Access Flow

1. **Initial Route Access**:
   - User attempts to access protected route (e.g., `/admin/users`)
   - Template decorator triggers `set_redirect` to store intended destination
   - `sync_auth_state` checks authentication status

2. **Authentication Process**:
   - If not authenticated:
     - Redirects to sign-in page
     - Preserves original destination in `redirect_after_login`
   - If authenticated:
     - Syncs Clerk user data with internal database
     - Updates user role (admin/user)
     - Redirects to original destination

3. **Component Rendering**:
   - Template checks route requirements from `template_config.py`
   - For unauthorized users: shows profile component with sign-in
   - For authorized users: renders protected content
   - For insufficient permissions: shows access denied page

### Adding New Protected Pages

1. Create a new page in the `pages` directory
2. Use the `@template` decorator with auth requirements:
   ```python
   @template(
       route="/protected/route",
       requires_auth=True,     # Requires authentication
       requires_admin=False    # Accessible to all users
   )
   def protected_page():
       return rx.vstack(...)
   ```
3. Add the route to `NAV_ITEMS` in `template_config.py`
4. Authentication and authorization will be automatically handled

### Modifying User Roles

1. Update `UserType` enum in `models/user.py`
2. Add corresponding checks in `UserState`
3. Update route requirements in `template_config.py`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this in your own projects!
