from fastapi import FastAPI

from backend.app.routes.health import router as health_router
from backend.app.routes.version import router as version_router
from backend.app.settings import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.api_version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
    app.include_router(health_router)
    app.include_router(version_router)
    return app


app = create_app()

