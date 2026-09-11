# ─────────────────────────────────────────────
# Stage 1: Install Python dependencies
# ─────────────────────────────────────────────
FROM python:3.12-slim AS deps

WORKDIR /tmp

COPY backend/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt


# ─────────────────────────────────────────────
# Stage 2: Final application image
# ─────────────────────────────────────────────
FROM python:3.12-slim

# OpenCV runtime libraries
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*


# Copy installed Python packages
COPY --from=deps /usr/local/lib/python3.12/site-packages \
    /usr/local/lib/python3.12/site-packages

COPY --from=deps /usr/local/bin \
    /usr/local/bin


# ─────────────────────────────────────────────
# Application directory
# ─────────────────────────────────────────────
WORKDIR /app


# Backend
COPY backend/app ./app


# ML code
COPY ml ./ml


# Trained model
COPY models/emotion_model.keras ./models/
COPY models/labels.json ./models/
COPY models/metrics.json ./models/


# ─────────────────────────────────────────────
# Environment variables
# ─────────────────────────────────────────────
ENV EMOTIONVISION_MODELS_DIR=/app/models
ENV EMOTIONVISION_ML_DIR=/app/ml


# Render provides PORT automatically
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}"]