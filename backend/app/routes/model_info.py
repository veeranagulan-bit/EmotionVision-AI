"""backend/app/routes/model_info.py — GET /model-info

Serves the real metrics.json produced by ml/train.py + ml/evaluate.py so
the frontend's "Model" page can display actual measured numbers instead of
anything fabricated. Returns 404 (not fake data) if training hasn't
happened yet.
"""

import json
import os

from fastapi import APIRouter, HTTPException

from app.config import METRICS_PATH
from app.services.emotion_model import get_predictor

router = APIRouter(tags=["model"])


@router.get("/model-info", summary="Real training/evaluation metrics, or 404 if not trained yet")
def model_info() -> dict:
    predictor = get_predictor()

    if not os.path.exists(METRICS_PATH):
        raise HTTPException(
            status_code=404,
            detail="No metrics found yet. Train the model first with "
                   "`python ml/train.py` (and optionally `python ml/evaluate.py` "
                   "for the full per-class report).",
        )

    with open(METRICS_PATH) as f:
        metrics = json.load(f)

    metrics["model_loaded"] = predictor.is_loaded
    return metrics
