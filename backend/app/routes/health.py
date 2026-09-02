"""backend/app/routes/health.py — GET /health"""

from fastapi import APIRouter

from app.config import APP_VERSION
from app.schemas.prediction import HealthResponse
from app.services.emotion_model import get_predictor

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    predictor = get_predictor()
    return HealthResponse(
        status="ok",
        model_loaded=predictor.is_loaded,
        classes=predictor.class_names if predictor.is_loaded else [],
        version=APP_VERSION,
    )
