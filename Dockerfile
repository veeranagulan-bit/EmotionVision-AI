# ── Stage 1: Install Python dependencies ──────────────────────────
FROM python:3.12-slim AS deps

WORKDIR /tmp
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Stage 2: Final image ─────────────────────────────────────────
FROM python:3.12-slim

# System libs required by opencv-python-headless at runtime
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from the deps stage
COPY --from=deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin

# Copy backend source code
WORKDIR /app
COPY backend/app ./app

# Copy trained model + labels + metrics into the image
COPY models/emotion_model.keras ./models/
COPY models/labels.json         ./models/
COPY models/metrics.json        ./models/

# Tell the backend where to find the model
ENV EMOTIONVISION_MODELS_DIR=/app/models

# Render uses port 10000 by default
EXPOSE 10000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
