"""
ml/predict.py

Standalone inference: given an image path, detects every face, classifies
the expression of each one using the trained model, and prints the results.
This module's `EmotionPredictor` class is also imported directly by the
FastAPI backend (backend/app/services/emotion_model.py) so training-time
and serving-time preprocessing can never drift apart.

CLI usage:
    python ml/predict.py path/to/image.jpg
"""

import os
import sys

import cv2
import numpy as np
import tensorflow as tf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import MODEL_PATH, LABELS_PATH, IMAGE_SIZE, CONFIDENCE_THRESHOLD, BACKBONE  # noqa: E402
from face_detector import FaceDetector, DetectedFace  # noqa: E402
from utils import load_json, fail  # noqa: E402

# Must match the preprocessing function baked into the saved model's
# Lambda layer (see ml/train.py PREPROCESS_FNS). Keras 3's safe
# deserialization can't resolve a bare reference to a builtin function
# like `preprocess_input` on its own, so we hand it back explicitly via
# custom_objects when loading.
PREPROCESS_FNS = {
    "mobilenetv3": tf.keras.applications.mobilenet_v3.preprocess_input,
    "efficientnetb0": tf.keras.applications.efficientnet.preprocess_input,
    "resnet50": tf.keras.applications.resnet50.preprocess_input,
}


class ModelNotLoadedError(RuntimeError):
    """Raised when a prediction is requested but no trained model is available yet."""


class EmotionPredictor:
    """
    Loads the trained model + label list once, and exposes a single
    `predict(image_bgr)` method that returns per-face results. Used by both
    the CLI below and the FastAPI backend.
    """

    def __init__(self, model_path: str = MODEL_PATH, labels_path: str = LABELS_PATH,
                 detector: str = "haar", confidence_threshold: float = CONFIDENCE_THRESHOLD):
        self.model_path = model_path
        self.labels_path = labels_path
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.class_names: list[str] = []
        self.face_detector = FaceDetector(detector=detector)
        self._try_load()

    def _try_load(self) -> None:
        if os.path.exists(self.model_path) and os.path.exists(self.labels_path):
            self.model = tf.keras.models.load_model(
                self.model_path,
                custom_objects={"preprocess_input": PREPROCESS_FNS[BACKBONE]},
            )
            self.class_names = load_json(self.labels_path)["labels"]

    @property
    def is_loaded(self) -> bool:
        return self.model is not None

    def reload(self) -> None:
        """Re-check disk for a model — useful after training completes
        without restarting the backend process."""
        self._try_load()

    def _preprocess_face(self, face_crop_bgr: np.ndarray) -> np.ndarray:
        face_rgb = cv2.cvtColor(face_crop_bgr, cv2.COLOR_BGR2RGB)
        face_resized = cv2.resize(face_rgb, IMAGE_SIZE)
        # NOTE: normalization matches the Lambda(preprocess_input) layer
        # baked into the saved Keras model, so raw 0-255 float input is
        # correct here — do not double-normalize.
        return face_resized.astype(np.float32)

    def predict(self, image_bgr: np.ndarray) -> dict:
        """
        Detect faces and classify each one.

        Returns a dict shaped like the API's /predict response:
            {
              "faces_detected": int,
              "predictions": [
                {"face_id", "box", "emotion", "confidence", "probabilities", "is_uncertain"}
              ]
            }
        Raises ModelNotLoadedError if no trained model has been produced yet.
        """
        if not self.is_loaded:
            raise ModelNotLoadedError(
                "No trained emotion model found. Run `python ml/train.py` "
                "to train one, then restart the backend."
            )

        faces = self.face_detector.detect(image_bgr)
        predictions = []
        if faces:
            batch = np.stack([self._preprocess_face(f.crop(image_bgr)) for f in faces])
            probs_batch = self.model.predict(batch, verbose=0)

            for i, (face, probs) in enumerate(zip(faces, probs_batch)):
                top_idx = int(np.argmax(probs))
                top_conf = float(probs[top_idx])
                predictions.append({
                    "face_id": i + 1,
                    "box": {"x": face.x, "y": face.y, "w": face.w, "h": face.h},
                    "emotion": self.class_names[top_idx],
                    "confidence": top_conf,
                    "is_uncertain": top_conf < self.confidence_threshold,
                    "probabilities": {
                        self.class_names[j]: float(probs[j]) for j in range(len(self.class_names))
                    },
                })

        return {"faces_detected": len(faces), "predictions": predictions}


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python ml/predict.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]
    image = cv2.imread(image_path)
    if image is None:
        fail(f"Could not read image: {image_path}")

    predictor = EmotionPredictor()
    if not predictor.is_loaded:
        fail(
            "No trained model found. Train one first with:\n\n"
            "    python ml/train.py\n"
        )

    result = predictor.predict(image)
    print(f"Faces detected: {result['faces_detected']}\n")
    for pred in result["predictions"]:
        tag = " (uncertain)" if pred["is_uncertain"] else ""
        print(f"Face {pred['face_id']} @ {pred['box']}: {pred['emotion']} "
              f"({pred['confidence'] * 100:.1f}%){tag}")
        for emotion, p in sorted(pred["probabilities"].items(), key=lambda kv: -kv[1]):
            print(f"    {emotion:10s} {p * 100:5.1f}%")
        print()


if __name__ == "__main__":
    main()