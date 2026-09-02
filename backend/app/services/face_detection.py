"""
backend/app/services/face_detection.py

Re-exports ml.face_detector.FaceDetector for any backend code that needs
face detection directly (outside of a full emotion prediction). Emotion
prediction itself goes through services/emotion_model.py, which already
performs detection internally as the first pipeline stage.
"""

import os
import sys

ML_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ml")
sys.path.insert(0, os.path.abspath(ML_DIR))

from face_detector import FaceDetector, DetectedFace  # noqa: E402,F401

__all__ = ["FaceDetector", "DetectedFace"]
