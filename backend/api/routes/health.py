import os
from fastapi import APIRouter
from datetime import datetime

try:
    from backend.api.schemas import HealthResponse
except ImportError:
    from api.schemas import HealthResponse

from prism.config import DB_PATH

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
def get_health():
    db_ok = os.path.exists(DB_PATH)
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "database": "connected" if db_ok else "ready",
        "prism_engine": "online"
    }
