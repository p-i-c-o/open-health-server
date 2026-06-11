from fastapi import APIRouter

router = APIRouter(tags=["system"])


@router.get("/health")
def read_health() -> dict[str, str]:
    return {"status": "ok"}

