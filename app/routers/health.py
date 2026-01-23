from fastapi import APIRouter
from app.schemas.health import HealthCheck

router = APIRouter()

@router.get("/health", response_model=HealthCheck)
async def health_check():
    return {"status": "ok hello Dushyant", "version": "0.1.0"}
