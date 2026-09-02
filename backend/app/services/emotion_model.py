"""
backend/app/services/emotion_model.py

Wraps ml.predict.EmotionPredictor as a process-wide singleton so the model
and label list are loaded once at backend startup, not on every request.
This is the ONLY place the backend talks to the trained model — it never
re-implements prediction logic, so training-time and serving-time
preprocessing can't drift apart.
"""

import os
import sys

# Make the sibling ml/ package importable without turning this repo into an
# installed package — keeps `python ml/train.py` and the backend in sync
# on one implementation of preprocessing + inference.
ML_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ml")
sys.path.insert(0, os.path.abspath(ML_DIR))

from predict import EmotionPredictor, ModelNotLoadedError  # noqa: E402
from app.config import MODEL_PATH, LABELS_PATH, CONFIDENCE_THRESHOLD, FACE_DETECTOR  # noqa: E402

__all__ = ["get_predictor", "ModelNotLoadedError"]

_predictor: EmotionPredictor | None = None


def get_predictor() -> EmotionPredictor:
    """Lazily create (once) and return the shared EmotionPredictor instance."""
    global _predictor
    if _predictor is None:
        _predictor = EmotionPredictor(
            model_path=MODEL_PATH,
            labels_path=LABELS_PATH,
            detector=FACE_DETECTOR,
            confidence_threshold=CONFIDENCE_THRESHOLD,
        )
    return _predictor
