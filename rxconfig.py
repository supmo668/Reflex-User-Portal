import reflex as rx
import app.config as CONFIG

backend_host = os.getenv("BACKEND_HOST", "0.0.0.0")
api_url = os.getenv("REFLEX_API_URL", "http://localhost:8000")
deploy_url = os.getenv("FRONTEND_DEPLOY_URL", os.getenv("RAILWAY_PUBLIC_DOMAIN", "http://localhost:3000"))
os.environ["FRONTEND_DEPLOY_URL"] = deploy_url

if deploy_url and not deploy_url.startswith("http"):
    deploy_url = f"https://{deploy_url}"

# CORS origins
cors_origins = [deploy_url]  # Allow the public domain for CORS
if frontend_origin := os.getenv("RAILWAY_PUBLIC_DOMAIN"):
    cors_origins.append(frontend_origin)

config = rx.Config(
    app_name=os.getenv("REFLEX_APP_NAME", "app"),
    app_module_import="app.reflex_app",
    show_built_with_reflex=False,
    tailwind=None,
    db_url=CONFIG.DATABASE_URL
)
print(f"Configuring Reflex with database URL: {CONFIG.DATABASE_URL.split('://')[0]}://<hidden>")  # Hide password in logs