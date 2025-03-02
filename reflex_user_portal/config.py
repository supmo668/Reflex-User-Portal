"""Configuration settings for the application."""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# App configuration
APP_DISPLAY_NAME = os.getenv("APP_DISPLAY_NAME", "SpyGlass Portal")
APP_ENV = os.getenv("APP_ENV", "DEV")

# Admin configuration
ADMIN_USER_EMAIL = os.getenv("ADMIN_USER_EMAIL")

# Clerk configuration
CLERK_PUBLISHABLE_KEY = os.getenv("CLERK_PUBLISHABLE_KEY")
CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")

# Database configuration
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_CONN_URI = os.getenv("DB_CONN_URI", "").replace("{YOUR-PASSWORD}", DB_PASSWORD) if DB_PASSWORD else None
DB_LOCAL_URI = os.getenv("DB_LOCAL_URI", "sqlite:///local.db")

# Use local database in development, otherwise use production database
DATABASE_URL = DB_LOCAL_URI if APP_ENV == "DEV" else DB_CONN_URI