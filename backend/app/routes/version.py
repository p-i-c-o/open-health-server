from fastapi import APIRouter

from backend.app.settings import get_settings

router = APIRouter(tags=["system"])


@router.get("/version")
def read_version() -> dict[str, str]:
    settings = get_settings()
    return {
        "app": settings.app_name,
        "version": settings.api_version,
        "environment": settings.environment,
    }

