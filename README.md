# EmotionVision AI — Human Facial Emotion Detection System

**Understand emotions through AI-powered facial expression analysis.**

EmotionVision AI is an end-to-end computer-vision web application: upload a
photo, it detects every human face in the image, and a transfer-learning CNN
predicts the facial expression of each one with a full confidence
breakdown.

> **A note on what this actually measures:** the model classifies the visual
> pattern of a facial expression. It does not, and cannot, determine a
> person's true internal emotional state. Every result is labeled a
> *predicted facial expression*, and low-confidence predictions are shown as
> "Uncertain" rather than forced into a category. See [Responsible AI](#responsible-ai--limitations).

---

## Features

- 🎯 Multi-face detection with an independent prediction per face
- 📊 Full probability distribution across every emotion class, not just the top label
- ⚠️ Configurable confidence threshold — low-confidence results are flagged, never faked
- 🌗 Dark / light mode with a persisted preference
- 🔒 Privacy-first: images are processed in memory and are not stored by default
- 🧪 Real, generated training metrics (accuracy, precision/recall/F1, confusion matrix) — nothing fabricated
- 🧱 Clean separation of ML pipeline, API, and frontend, each independently runnable

## Tech stack

| Layer | Technology |
|---|---|
| ML / training | Python, TensorFlow/Keras, OpenCV, scikit-learn, Matplotlib, Seaborn |
| Backend API | FastAPI, Uvicorn |
| Frontend | React, Vite, TypeScript, Tailwind CSS, Framer Motion, Recharts, Lucide |

## Architecture

```text
Browser (React)
      │  POST /predict (image file)
      ▼
FastAPI backend
      │
      ├─ Face detection (OpenCV)
      ├─ Crop + preprocess each face
      ├─ Emotion model inference (Keras)
      └─ JSON response (per-face predictions + probabilities)
      ▼
React dashboard renders bounding boxes, primary result, and charts
```

```text
ml/                  Training pipeline: dataset prep, training, evaluation, inference
backend/              FastAPI app that serves the trained model
frontend/             React + Vite + TypeScript + Tailwind dashboard
data/                 Where you place the downloaded Kaggle dataset (gitignored)
models/               Where the trained model + real metrics are written (large binary gitignored)
```

---

## Project structure

```text
emotionvision-ai/
│
├── frontend/
│   ├── src/
│   │   ├── components/     UploadBox, ResultCard, EmotionChart, FaceCard, Navbar, ...
│   │   ├── pages/           Home, Analyze, HowItWorks, Model, About
│   │   ├── hooks/            useTheme
│   │   ├── services/         api.ts (fetch wrapper, reads VITE_API_URL)
│   │   ├── types/             shared TS types mirroring the backend schemas
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
│
├── backend/
│   ├── app/
│   │   ├── main.py            FastAPI app, CORS, static asset mount
│   │   ├── config.py          env-driven configuration
│   │   ├── routes/            health.py, prediction.py, model_info.py
│   │   ├── services/          emotion_model.py, face_detection.py
│   │   ├── schemas/           Pydantic request/response models
│   │   └── utils/              image validation/decoding
│   ├── tests/                  pytest suite
│   └── requirements.txt
│
├── ml/
│   ├── config.py               single source of truth for paths & hyperparameters
│   ├── preprocess.py           raw Kaggle download → train/validation/test folders
│   ├── dataset.py               tf.data pipelines, class distribution, corruption scan
│   ├── train.py                  transfer learning + fine-tuning
│   ├── evaluate.py                real metrics, confusion matrix, classification report
│   ├── predict.py                  shared inference class (used by CLI and the backend)
│   ├── face_detector.py             OpenCV face detection
│   └── utils.py
│
├── data/                 (gitignored — see data/README.md)
├── models/                (large model file gitignored — see models/README.md)
├── screenshots/
├── .gitignore
├── LICENSE
└── README.md
```

---

## Dataset

Uses a public Kaggle facial-expression dataset — **FER-2013** by default,
or any similarly-structured Kaggle dataset. **The dataset is not included in
this repository.**

**Full instructions: [`data/README.md`](data/README.md).** Short version:

```bash
# 1. Download FER-2013 from Kaggle, unzip into data/raw/
# 2. Convert it into the required train/validation/test structure:
python ml/preprocess.py
# 3. Inspect it — class distribution, dimensions, corrupted-file scan:
python ml/dataset.py
```

The pipeline never hard-codes class names or counts — everything is derived
from the folders that actually exist under `data/train/`.

---

## Installation

### Prerequisites

- Python 3.10–3.11
- Node.js 18+
- ~2GB free disk space for the FER-2013 dataset and dependencies

### 1. Clone and set up the ML environment

```bash
cd ml
python -m venv venv
```

Windows (PowerShell):

```powershell
.\venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
source venv/bin/activate
```

```bash
pip install -r requirements.txt
```

### 2. Set up the backend

```bash
cd backend
python -m venv venv
```

Windows (PowerShell):

```powershell
.\venv\Scripts\Activate.ps1
```

```bash
pip install -r requirements.txt
cp .env.example .env
```

### 3. Set up the frontend

```bash
cd frontend
npm install
cp .env.example .env
```

---

## Training the model

1. Make sure `data/train`, `data/validation`, `data/test` exist (see
   [Dataset](#dataset) above).
2. From the project root, with the `ml` virtual environment active:

   ```bash
   python ml/train.py
   ```

   This trains the classification head first, then fine-tunes the top
   layers of the backbone, and saves:
   - `models/emotion_model.keras` — the trained model
   - `models/labels.json` — the real class list, in the model's output order
   - `models/metrics.json` — accuracy/loss/AUC actually measured on the test set
   - `models/training_history.png` — accuracy/loss curves

3. Run the full evaluation for per-class precision/recall/F1 and a
   confusion matrix:

   ```bash
   python ml/evaluate.py
   ```

   This updates `models/metrics.json` and writes
   `models/confusion_matrix.png`.

To change the backbone (`mobilenetv3` / `efficientnetb0` / `resnet50`) or
any hyperparameter, edit `ml/config.py` or set the `EMOTIONVISION_BACKBONE`
environment variable.

### Class imbalance

`ml/train.py` computes real inverse-frequency class weights from your
actual training set (see `ml/dataset.py:compute_class_weights`) and applies
them during training — disable with `USE_CLASS_WEIGHTS = False` in
`ml/config.py` if you'd rather rely on augmentation alone.

---

## Running the backend

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

- API root: <http://localhost:8000>
- Interactive Swagger docs: <http://localhost:8000/docs>

If no trained model is present yet, `/health` reports
`"model_loaded": false` and `/predict` returns a `503` with a clear
message — the backend never fabricates a prediction.

### API reference

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | API info and endpoint list |
| `GET` | `/health` | Model-loaded status and detected classes |
| `POST` | `/predict` | Upload an image, get per-face predictions |
| `GET` | `/model-info` | Real training/evaluation metrics (404 until trained) |
| `GET` | `/assets/*` | Static training charts (confusion matrix, etc.) |

`POST /predict` response shape:

```json
{
  "faces_detected": 1,
  "predictions": [
    {
      "face_id": 1,
      "box": { "x": 120, "y": 84, "w": 150, "h": 150 },
      "emotion": "Happy",
      "confidence": 0.9428,
      "is_uncertain": false,
      "probabilities": {
        "Happy": 0.9428, "Sad": 0.021, "Angry": 0.008,
        "Fear": 0.004, "Surprise": 0.013, "Disgust": 0.001, "Neutral": 0.010
      }
    }
  ]
}
```

---

## Running the frontend

```bash
cd frontend
npm run dev
```

Visit <http://localhost:5173>. Make sure `VITE_API_URL` in `frontend/.env`
points at your running backend (defaults to `http://localhost:8000`).

---

## Testing

### Backend

```bash
cd backend
pip install -r requirements-dev.txt
pytest
```

Covers the health endpoint and the error paths that don't require a
trained model (invalid file type, empty upload, no-model 503). Once you've
trained a model, you can extend `tests/test_prediction.py` with real
face / no-face / multiple-face fixture images.

### Frontend

```bash
cd frontend
npm run build   # type-checks with tsc -b, then produces a production build
```

### ML

```bash
python ml/dataset.py   # sanity-checks the dataset: classes, distribution, corrupted files
```

---

## Model performance

Real numbers, once you've trained a model, are visible at:

- **In the app:** the [Model](frontend/src/pages/Model.tsx) page (`/model`), which
  reads them live from `GET /model-info`.
- **On disk:** `models/metrics.json`, `models/confusion_matrix.png`,
  `models/training_history.png`, `models/class_distribution.png`.

This README does not print sample numbers here on purpose — see
[`ml/train.py`](ml/train.py) and [`ml/evaluate.py`](ml/evaluate.py) rather
than any hard-coded figure.

---

## Responsible AI & limitations

- Facial expression classification is **not** the same as reading a
  person's true emotions — it classifies a visual pattern, nothing more.
- Lighting, pose, occlusion, image quality, camera angle, cultural
  expression differences, and dataset bias can all affect predictions.
- Predictions are probabilistic; results below the confidence threshold
  are shown as "Uncertain" instead of being forced into a category.
- **Not for medical or psychological diagnosis.**
- **Not for hiring, policing, surveillance, insurance, or other high-impact
  decisions about real people.**
- This app performs facial *expression* classification only — it does
  **not** perform facial recognition or identity matching, and should not
  be adapted to do so.
- Images are processed in memory wherever possible and are not stored by
  the backend by default.

See the in-app [About](frontend/src/pages/About.tsx) page for the same
content presented to end users.

---

## Future improvements

Implemented in this repo: image upload, multi-face detection, emotion
classification with a confidence threshold, full training/evaluation
pipeline, REST API, and a responsive dashboard.

Not implemented, but natural next steps:

- Real-time webcam emotion analysis
- Video (frame-by-frame) emotion analysis
- Grad-CAM interpretability ("why this prediction?" heatmaps)
- ONNX export / ONNX Runtime or TensorFlow Lite for edge & mobile deployment
- Model quantization for faster CPU inference
- A more diverse, multi-dataset training set to reduce bias
- Model versioning / A-B comparison in the Model page

---

## Deployment

### Frontend

Deploy the `frontend/` directory to **Vercel** or **Netlify**:

```bash
cd frontend
npm run build   # outputs to frontend/dist
```

Set the `VITE_API_URL` environment variable in your hosting provider's
dashboard to your deployed backend's public URL.

### Backend

Deploy `backend/` to a Python-friendly host such as **Render** or
**Railway**:

- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Set `CORS_ORIGINS` to your deployed frontend's URL
- Set `EMOTIONVISION_MODELS_DIR` if you're mounting the model from a
  volume rather than shipping it in the image

### Model hosting

`models/emotion_model.keras` is not committed to this repository (see
[`models/README.md`](models/README.md)). For deployment, either:

- Bundle it into your backend's Docker image / build artifact, or
- Download it from a GitHub Release, Hugging Face Hub, or object storage
  (S3/GCS) as a startup step before `uvicorn` launches.

---

## Author

Built as a portfolio-quality demonstration of an end-to-end computer-vision
product — dataset preparation, transfer learning, a real API, and a
production-styled frontend, wired together honestly (no fabricated metrics,
no fake inference when a model isn't loaded).
