from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["Healthcheck Endpoint"])


@router.get("/health", tags=["health"])
async def health_check():
    return {"status": "UP"}
