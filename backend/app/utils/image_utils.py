"""backend/app/utils/image_utils.py — safe image decoding and validation."""

import cv2
import numpy as np
from fastapi import HTTPException, UploadFile

from app.config import ALLOWED_CONTENT_TYPES, MAX_UPLOAD_SIZE_BYTES


async def read_and_validate_image(file: UploadFile) -> np.ndarray:
    """
    Reads an uploaded file, validates its type and size, and safely decodes
    it into a BGR numpy array via OpenCV (never executes or trusts the file
    beyond pixel decoding).
    """
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail="Unsupported image format. Please upload JPG, PNG, or WEBP.",
        )

    raw_bytes = await file.read()

    if len(raw_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if len(raw_bytes) > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File is too large. Maximum upload size is "
                   f"{MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)}MB.",
        )

    np_buffer = np.frombuffer(raw_bytes, dtype=np.uint8)
    image = cv2.imdecode(np_buffer, cv2.IMREAD_COLOR)

    if image is None:
        raise HTTPException(
            status_code=422,
            detail="Could not decode this file as an image. It may be corrupted "
                   "or not a valid JPG/PNG/WEBP.",
        )

    return image
