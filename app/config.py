"""Configuration settings for the application."""
import os, warnings
from dotenv import load_dotenv

# Load environment variables
load_envar = load_dotenv()
if not load_envar:
    warnings.warn("Failed to load environment variables from .env file.")

# App configuration
APP_DISPLAY_NAME = os.getenv("REFLEX_APP_NAME", "App Portal")
REFLEX_ENV_MODE = os.getenv("APP_ENV", "DEV").upper()
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG" if REFLEX_ENV_MODE.upper() in ["DEV", "TEST", "Env.DEV"] else "INFO").upper()
print(f"App environment: {REFLEX_ENV_MODE}")

# Admin configuration
ADMIN_USER_EMAILS = os.getenv("ADMIN_USER_EMAILS", "").split(",")

# Clerk configuration
CLERK_PUBLISHABLE_KEY = os.getenv("CLERK_PUBLISHABLE_KEY")
CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")
CLERK_AUTHORIZED_DOMAINS = os.getenv("CLERK_AUTHORIZED_DOMAINS", "localhost:3000,*").split(",")
    # add railway frontend domain if needed
CLERK_AUTHORIZED_DOMAINS += [os.getenv("FRONTEND_URL", "")]

# Database configuration
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_CONN_URI = os.getenv("REFLEX_DB_URL", "").format(DB_PASSWORD=DB_PASSWORD) if DB_PASSWORD else os.getenv("REFLEX_DB_URL", "")
DB_LOCAL_URI = os.getenv("REFLEX_DB_URL", "sqlite:///app.db")

# if REFLEX_DB_URL not specified, use local database in development. Otherwise, stick to stick to REFLEX_DB_URL
DATABASE_URL = DB_LOCAL_URI if REFLEX_ENV_MODE == "DEV" else DB_CONN_URI

# API URL
API_URL = os.getenv("REFLEX_API_URL", os.getenv("API_URL", "http://localhost:8000"))

# Frontend URL - prioritize FRONTEND_DEPLOY_URL for backend services
FRONTEND_URL = (
    os.getenv("FRONTEND_DEPLOY_URL") or  # Railway deploy script sets this
    os.getenv("RAILWAY_PUBLIC_DOMAIN") or  # Railway auto-generated domain
    os.getenv("REFLEX_DEPLOY_URL") or  # Legacy fallback
    os.getenv("DEPLOY_URL") or  # Legacy fallback
    "http://localhost:3000"  # Development default
)
# Ensure FRONTEND_URL starts with http or https
if FRONTEND_URL and not FRONTEND_URL.startswith("http"):
    FRONTEND_URL = f"https://{FRONTEND_URL}"

# Admin Config table name registered in models/ at MODEL_FACTORY
ADMIN_CONFIG_TABLE_NAME = "admin_config"
ADMIN_CONFIG_TABLE_JSON_CONFIG_COL = "configuration"