"""
ml/face_detector.py

Face detection used before emotion classification, both here in the ML
scripts and (via the same class) inside the FastAPI backend.

Default detector: OpenCV's DNN face detector (a small, reasonably accurate
res10 SSD model shipped with opencv-data / downloaded on first use), with
a Haar Cascade fallback that always ships with opencv-python so the app
still works out of the box with zero extra downloads.
"""

import os
from dataclasses import dataclass

import cv2
import numpy as np


@dataclass
class DetectedFace:
    x: int
    y: int
    w: int
    h: int
    confidence: float

    def crop(self, image: np.ndarray, margin: float = 0.15) -> np.ndarray:
        """Crop the face out of `image` with a small margin around the box."""
        img_h, img_w = image.shape[:2]
        mx, my = int(self.w * margin), int(self.h * margin)
        x1 = max(self.x - mx, 0)
        y1 = max(self.y - my, 0)
        x2 = min(self.x + self.w + mx, img_w)
        y2 = min(self.y + self.h + my, img_h)
        return image[y1:y2, x1:x2]


class FaceDetector:
    """
    Thin wrapper so the rest of the codebase doesn't care which underlying
    detector is active. Uses OpenCV's Haar Cascade by default (zero external
    downloads, works everywhere); pass detector="dnn" to use the more
    accurate SSD-based detector if its weight files are present.
    """

    def __init__(self, detector: str = "haar", min_confidence: float = 0.6):
        self.detector_type = detector
        self.min_confidence = min_confidence

        if detector == "haar":
            cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            self._cascade = cv2.CascadeClassifier(cascade_path)
            if self._cascade.empty():
                raise RuntimeError(f"Could not load Haar cascade from {cascade_path}")
        elif detector == "dnn":
            proto = os.environ.get("FACE_DNN_PROTO", "")
            model = os.environ.get("FACE_DNN_MODEL", "")
            if not (proto and model and os.path.exists(proto) and os.path.exists(model)):
                raise RuntimeError(
                    "DNN face detector requested but FACE_DNN_PROTO / "
                    "FACE_DNN_MODEL weight files were not found. Falling back "
                    "to detector='haar' is recommended unless you've downloaded "
                    "the res10 SSD weights."
                )
            self._net = cv2.dnn.readNetFromCaffe(proto, model)
        else:
            raise ValueError(f"Unknown detector type: {detector}")

    def detect(self, image_bgr: np.ndarray) -> list[DetectedFace]:
        if self.detector_type == "haar":
            return self._detect_haar(image_bgr)
        return self._detect_dnn(image_bgr)

    def _detect_haar(self, image_bgr: np.ndarray) -> list[DetectedFace]:
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        boxes = self._cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=6, minSize=(48, 48)
        )
        # Haar doesn't give a confidence score — report a fixed high value
        # since every returned box already passed the neighbor threshold.
        return [DetectedFace(int(x), int(y), int(w), int(h), 0.99) for (x, y, w, h) in boxes]

    def _detect_dnn(self, image_bgr: np.ndarray) -> list[DetectedFace]:
        h, w = image_bgr.shape[:2]
        blob = cv2.dnn.blobFromImage(
            cv2.resize(image_bgr, (300, 300)), 1.0, (300, 300),
            (104.0, 177.0, 123.0),
        )
        self._net.setInput(blob)
        detections = self._net.forward()

        faces = []
        for i in range(detections.shape[2]):
            confidence = float(detections[0, 0, i, 2])
            if confidence < self.min_confidence:
                continue
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            x1, y1, x2, y2 = box.astype(int)
            x1, y1 = max(x1, 0), max(y1, 0)
            faces.append(DetectedFace(int(x1), int(y1), int(x2 - x1), int(y2 - y1), confidence))
        return faces


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python ml/face_detector.py <image_path>")
        sys.exit(1)

    img = cv2.imread(sys.argv[1])
    if img is None:
        print(f"Could not read image: {sys.argv[1]}")
        sys.exit(1)

    detector = FaceDetector(detector="haar")
    faces = detector.detect(img)
    print(f"Detected {len(faces)} face(s):")
    for f in faces:
        print(f"  x={f.x} y={f.y} w={f.w} h={f.h} confidence={f.confidence:.2f}")
