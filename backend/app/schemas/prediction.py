"""backend/app/schemas/prediction.py — Pydantic models for the /predict API."""

from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    x: int
    y: int
    w: int
    h: int


class FacePrediction(BaseModel):
    face_id: int
    box: BoundingBox
    emotion: str = Field(..., description="Predicted facial expression label")
    confidence: float = Field(..., description="Softmax probability of the top class, 0-1")
    is_uncertain: bool = Field(
        ..., description="True when confidence is below CONFIDENCE_THRESHOLD"
    )
    probabilities: dict[str, float] = Field(
        ..., description="Full probability distribution across all emotion classes"
    )


class PredictionResponse(BaseModel):
    faces_detected: int
    predictions: list[FacePrediction]


class ErrorResponse(BaseModel):
    detail: str


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    classes: list[str] = []
    version: str
