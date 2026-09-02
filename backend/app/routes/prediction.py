"""backend/app/routes/prediction.py — POST /predict"""

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.prediction import PredictionResponse
from app.services.emotion_model import get_predictor, ModelNotLoadedError
from app.utils.image_utils import read_and_validate_image

router = APIRouter(tags=["prediction"])


@router.post(
    "/predict",
    response_model=PredictionResponse,
    responses={
        400: {"description": "Empty or invalid upload"},
        413: {"description": "File too large"},
        415: {"description": "Unsupported image format"},
        422: {"description": "Could not decode image"},
        503: {"description": "Model not loaded — training required first"},
    },
    summary="Detect faces and classify the facial expression of each one",
)
async def predict(file: UploadFile = File(..., description="JPG, PNG, or WEBP image")) -> PredictionResponse:
    image = await read_and_validate_image(file)
    predictor = get_predictor()

    try:
        result = predictor.predict(image)
    except ModelNotLoadedError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return PredictionResponse(**result)
