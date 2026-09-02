"""
Central configuration for the EmotionVision AI machine-learning pipeline.

Every path, hyperparameter, and label list used by dataset.py, preprocess.py,
train.py, evaluate.py, and predict.py is defined here so the pipeline never
hard-codes assumptions about where the dataset lives or how many classes
it has.

Edit DATA_DIR (or set the EMOTIONVISION_DATA_DIR env var) to point at
wherever you unzip the Kaggle dataset.
"""

import os

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ML_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(ML_DIR)

# Where the prepared dataset lives, in ImageFolder-style structure:
#   data/train/<class_name>/*.jpg
#   data/validation/<class_name>/*.jpg
#   data/test/<class_name>/*.jpg
# See ml/preprocess.py if your raw Kaggle download does not already look
# like this (e.g. raw FER-2013 CSV, or only "train" + "test" folders).
DATA_DIR = os.environ.get("EMOTIONVISION_DATA_DIR", os.path.join(PROJECT_ROOT, "data"))
TRAIN_DIR = os.path.join(DATA_DIR, "train")
VAL_DIR = os.path.join(DATA_DIR, "validation")
TEST_DIR = os.path.join(DATA_DIR, "test")

# Where raw Kaggle files should be dropped before running preprocess.py
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")

MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
MODEL_PATH = os.path.join(MODELS_DIR, "emotion_model.keras")
BEST_CHECKPOINT_PATH = os.path.join(MODELS_DIR, "checkpoints", "best_model.keras")
LABELS_PATH = os.path.join(MODELS_DIR, "labels.json")
METRICS_PATH = os.path.join(MODELS_DIR, "metrics.json")
CONFUSION_MATRIX_PATH = os.path.join(MODELS_DIR, "confusion_matrix.png")
TRAINING_HISTORY_PATH = os.path.join(MODELS_DIR, "training_history.png")
CLASS_DISTRIBUTION_PATH = os.path.join(MODELS_DIR, "class_distribution.png")

# ---------------------------------------------------------------------------
# Image / model parameters
# ---------------------------------------------------------------------------
IMAGE_SIZE = (224, 224)     # required input size for the transfer-learning backbone
CHANNELS = 3
BATCH_SIZE = 32
SEED = 42

# Backbone choices: "mobilenetv3" (fastest, best for CPU/edge), "efficientnetb0",
# or "resnet50". MobileNetV3 is the default because it trains and serves well
# without a GPU, which keeps the project runnable on a laptop.
BACKBONE = os.environ.get("EMOTIONVISION_BACKBONE", "mobilenetv3")

# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------
EPOCHS_HEAD = 15          # epochs training only the new classification head
EPOCHS_FINE_TUNE = 15     # epochs fine-tuning the unfrozen top backbone layers
LEARNING_RATE_HEAD = 1e-3
LEARNING_RATE_FINE_TUNE = 1e-5
FINE_TUNE_UNFREEZE_LAYERS = 30   # number of final backbone layers to unfreeze
EARLY_STOPPING_PATIENCE = 5
REDUCE_LR_PATIENCE = 3
REDUCE_LR_FACTOR = 0.5
USE_CLASS_WEIGHTS = True

# ---------------------------------------------------------------------------
# Data augmentation (kept realistic — see ml/dataset.py for rationale)
# ---------------------------------------------------------------------------
AUGMENTATION = {
    "horizontal_flip": True,
    "rotation_range": 10,       # degrees
    "zoom_range": 0.10,
    "width_shift_range": 0.08,
    "height_shift_range": 0.08,
    "brightness_range": (0.9, 1.1),
}

# ---------------------------------------------------------------------------
# Inference
# ---------------------------------------------------------------------------
CONFIDENCE_THRESHOLD = 0.50   # below this, the UI shows "Uncertain / Low Confidence"

# ---------------------------------------------------------------------------
# Emotion labels
# ---------------------------------------------------------------------------
# This is a DEFAULT label set matching the standard FER-2013 dataset, used
# only as a fallback / for documentation. dataset.py always re-derives the
# real label list from the folder names found under TRAIN_DIR, and train.py
# writes that authoritative list to LABELS_PATH. The backend loads labels
# from LABELS_PATH, never from this constant, so the app can never silently
# mismatch the model's output indices and the dataset's real classes.
DEFAULT_EMOTION_LABELS = [
    "Angry",
    "Disgust",
    "Fear",
    "Happy",
    "Neutral",
    "Sad",
    "Surprise",
]
