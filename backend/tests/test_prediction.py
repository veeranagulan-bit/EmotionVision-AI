"""
backend/tests/test_prediction.py

Covers the error paths that don't require a trained model (invalid file
type, empty upload) plus the "model not loaded" 503 path. Full end-to-end
prediction tests (real face / no-face / multiple-face images) require a
trained model at models/emotion_model.keras — see the README's "Testing"
section for how to run those once you've trained one.
"""

import io

from fastapi.testclient import TestClient
from PIL import Image

from app.main import app

client = TestClient(app)


def _make_png_bytes(size=(64, 64), color=(255, 0, 0)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", size, color).save(buf, format="PNG")
    buf.seek(0)
    return buf.read()


def test_predict_rejects_unsupported_content_type():
    response = client.post(
        "/predict",
        files={"file": ("note.txt", b"hello world", "text/plain")},
    )
    assert response.status_code == 415


def test_predict_rejects_empty_file():
    response = client.post(
        "/predict",
        files={"file": ("empty.png", b"", "image/png")},
    )
    assert response.status_code == 400


def test_predict_without_trained_model_returns_503_or_result():
    """
    If no model has been trained yet in this environment, the API must
    respond with a clear 503 rather than a fake prediction. If a model
    *has* been trained, a plain solid-color image should simply yield
    zero detected faces.
    """
    png_bytes = _make_png_bytes()
    response = client.post(
        "/predict",
        files={"file": ("plain.png", png_bytes, "image/png")},
    )
    assert response.status_code in (200, 503)
    if response.status_code == 200:
        body = response.json()
        assert body["faces_detected"] == 0
        assert body["predictions"] == []
