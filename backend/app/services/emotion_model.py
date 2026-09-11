"""
backend/app/services/emotion_model.py

Wraps ml.predict.EmotionPredictor as a process-wide singleton so the model
and label list are loaded once at backend startup, not on every request.
"""

import os
import sys
from pathlib import Path

# ---------------------------------------------------------
# Locate the ML directory
# ---------------------------------------------------------
# Docker:
#   /app/ml
#
# Local project:
#   project_root/ml
# ---------------------------------------------------------

ML_DIR = os.environ.get("EMOTIONVISION_ML_DIR")

if ML_DIR:
    ML_DIR = Path(ML_DIR)
else:
    ML_DIR = Path(__file__).resolve().parents[3] / "ml"

# Make ml/ importable
sys.path.insert(0, str(ML_DIR))

# Import prediction logic from ml/predict.py
from predict import EmotionPredictor, ModelNotLoadedError  # noqa: E402

from app.config import (  # noqa: E402
    MODEL_PATH,
    LABELS_PATH,
    CONFIDENCE_THRESHOLD,
    FACE_DETECTOR,
)

__all__ = ["get_predictor", "ModelNotLoadedError"]

# ---------------------------------------------------------
# Process-wide predictor singleton
# ---------------------------------------------------------

_predictor: EmotionPredictor | None = None


def get_predictor() -> EmotionPredictor:
    """Lazily create and return the shared EmotionPredictor instance."""
    global _predictor

    if _predictor is None:
        _predictor = EmotionPredictor(
            model_path=MODEL_PATH,
            labels_path=LABELS_PATH,
            detector=FACE_DETECTOR,
            confidence_threshold=CONFIDENCE_THRESHOLD,
        )

    return _predictor