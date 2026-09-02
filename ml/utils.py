"""Small shared helpers used across the ML pipeline scripts."""

import json
import os
import sys


def ensure_dir(path: str) -> None:
    """Create a directory (and parents) if it doesn't already exist."""
    os.makedirs(path, exist_ok=True)


def save_json(data: dict, path: str) -> None:
    ensure_dir(os.path.dirname(path))
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def load_json(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def fail(message: str) -> None:
    """Print a clear, actionable error and exit non-zero."""
    print(f"\n[EmotionVision AI] ERROR: {message}\n", file=sys.stderr)
    sys.exit(1)


def check_dataset_present(train_dir: str, val_dir: str, test_dir: str) -> None:
    """
    Fail fast with a helpful message if the dataset has not been downloaded
    and prepared yet, rather than letting a cryptic Keras error surface.
    """
    missing = [d for d in (train_dir, val_dir, test_dir) if not os.path.isdir(d)]
    if missing:
        fail(
            "Dataset not found at the expected location(s):\n  "
            + "\n  ".join(missing)
            + "\n\nDownload a facial-expression dataset from Kaggle (e.g. FER-2013) "
            "and either place it directly into data/train, data/validation, data/test "
            "(one subfolder per emotion class), or drop the raw download into "
            "data/raw and run:\n\n    python ml/preprocess.py\n\n"
            "See the project README's 'Dataset' section for exact steps."
        )
