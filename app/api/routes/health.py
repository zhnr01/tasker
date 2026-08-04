from fastapi import APIRouter

from app.config import get_settings

router = APIRouter(tags=["system"])


@router.get("/health")
def health() -> dict[str, str]:
    settings = get_settings()
    # Only expose non-sensitive fields. NEVER return SECRET_KEY / DATABASE_URL.
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
        "version": settings.PROJECT_NAME,
    }
