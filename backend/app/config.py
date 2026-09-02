"""
backend/app/config.py

Backend configuration, driven by environment variables so nothing (API
URLs, upload limits, CORS origins, model paths) is hard-coded across the
codebase. Copy backend/.env.example to backend/.env and adjust as needed.
"""

import os
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent

# Re-use the same models/ directory the ML pipeline writes to, so training
# and serving never fall out of sync.
MODELS_DIR = os.environ.get("EMOTIONVISION_MODELS_DIR", str(PROJECT_ROOT / "models"))
MODEL_PATH = os.path.join(MODELS_DIR, "emotion_model.keras")
LABELS_PATH = os.path.join(MODELS_DIR, "labels.json")
METRICS_PATH = os.path.join(MODELS_DIR, "metrics.json")

CONFIDENCE_THRESHOLD = float(os.environ.get("CONFIDENCE_THRESHOLD", 0.50))
FACE_DETECTOR = os.environ.get("FACE_DETECTOR", "haar")  # "haar" or "dnn"

# Upload limits
MAX_UPLOAD_SIZE_MB = int(os.environ.get("MAX_UPLOAD_SIZE_MB", 8))
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}

# CORS — comma-separated list of allowed frontend origins
CORS_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if origin.strip()
]

APP_NAME = "EmotionVision AI API"
APP_VERSION = "1.0.0"
