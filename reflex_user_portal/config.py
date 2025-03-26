"""Configuration settings for the application."""
import os, warnings
import logging
from dotenv import load_dotenv

# Load environment variables
load_envar = load_dotenv()
if not load_envar:
    warnings.warn("Failed to load environment variables from .env file.")

# App configuration
APP_DISPLAY_NAME = os.getenv("APP_DISPLAY_NAME", "App Portal")
APP_ENV = os.getenv("APP_ENV", "DEV").upper()
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG" if APP_ENV in ["DEV", "TEST"] else "INFO").upper()
print(f"App environment: {APP_ENV}")

# Admin configuration
ADMIN_USER_EMAILS = os.getenv("ADMIN_USER_EMAILS", "").split(",")

# Clerk configuration
CLERK_PUBLISHABLE_KEY = os.getenv("CLERK_PUBLISHABLE_KEY")
CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")

# Database configuration
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_CONN_URI = os.getenv("DB_CONN_URI", "").format(DB_PASSWORD=DB_PASSWORD) if DB_PASSWORD else None
DB_LOCAL_URI = os.getenv("DB_LOCAL_URI", "sqlite:///app.db")

# Use local database in development, otherwise use production database
DATABASE_URL = DB_LOCAL_URI if APP_ENV == "DEV" else DB_CONN_URI

# Admin Config table name registered in models/ at MODEL_FACTORY
ADMIN_CONFIG_TABLE_NAME = "admin_config"
ADMIN_CONFIG_TABLE_JSON_CONFIG_COL = "configuration"