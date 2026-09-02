"""
ml/preprocess.py

Converts a raw Kaggle facial-expression download into the
train/validation/test folder structure the rest of the pipeline expects:

    data/train/<emotion>/*.jpg
    data/validation/<emotion>/*.jpg
    data/test/<emotion>/*.jpg

This script handles the two most common shapes a Kaggle facial-expression
dataset arrives in:

1. CSV format (classic FER-2013: fer2013.csv with columns
   "emotion,pixels,Usage") — each row is a 48x48 grayscale image encoded as
   space-separated pixel values.

2. Folder-of-images format (many Kaggle re-uploads of FER-2013, and most
   other facial-expression datasets) that already look like:

       raw/train/<emotion>/*.jpg
       raw/test/<emotion>/*.jpg

   but with no validation split, or with a different split ratio than we
   want.

Usage:
    1. Download a dataset from Kaggle (see README "Dataset" section).
    2. Unzip it into data/raw/  (so e.g. data/raw/fer2013.csv, or
       data/raw/train/<emotion>/*.jpg exist).
    3. Run:  python ml/preprocess.py

The script never assumes class names in advance — it reads whatever class
folders / CSV label values are actually present.
"""

import csv
import os
import shutil
import sys

import numpy as np
from PIL import Image
from sklearn.model_selection import train_test_split

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import RAW_DATA_DIR, TRAIN_DIR, VAL_DIR, TEST_DIR, SEED  # noqa: E402
from utils import ensure_dir, fail  # noqa: E402

VAL_SPLIT = 0.15  # fraction of the training data held out for validation

# FER-2013's canonical numeric-to-label mapping (only used if a CSV with
# integer emotion codes, rather than named folders, is found).
FER2013_LABELS = {
    0: "Angry",
    1: "Disgust",
    2: "Fear",
    3: "Happy",
    4: "Sad",
    5: "Surprise",
    6: "Neutral",
}


def find_csv() -> str | None:
    for name in os.listdir(RAW_DATA_DIR) if os.path.isdir(RAW_DATA_DIR) else []:
        if name.lower().endswith(".csv"):
            return os.path.join(RAW_DATA_DIR, name)
    return None


def preprocess_from_csv(csv_path: str) -> None:
    print(f"Found CSV dataset: {csv_path}")
    print("Decoding pixel columns and writing per-class image folders...")

    ensure_dir(TRAIN_DIR)
    ensure_dir(VAL_DIR)
    ensure_dir(TEST_DIR)

    rows_by_usage = {"Training": [], "PublicTest": [], "PrivateTest": []}

    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            usage = row.get("Usage", "Training")
            rows_by_usage.setdefault(usage, []).append(row)

    def write_rows(rows, out_dir):
        for i, row in enumerate(rows):
            label = int(row["emotion"])
            label_name = FER2013_LABELS.get(label, str(label))
            pixels = np.array(row["pixels"].split(), dtype=np.uint8).reshape(48, 48)
            img = Image.fromarray(pixels, mode="L").convert("RGB")
            class_dir = os.path.join(out_dir, label_name)
            ensure_dir(class_dir)
            img.save(os.path.join(class_dir, f"{i:06d}.jpg"), quality=95)

    print(f"  Training rows:    {len(rows_by_usage['Training'])}")
    print(f"  PublicTest rows:  {len(rows_by_usage['PublicTest'])}")
    print(f"  PrivateTest rows: {len(rows_by_usage['PrivateTest'])}")

    # Split "Training" into train/validation; PublicTest+PrivateTest -> test
    train_rows, val_rows = train_test_split(
        rows_by_usage["Training"], test_size=VAL_SPLIT, random_state=SEED
    )
    test_rows = rows_by_usage["PublicTest"] + rows_by_usage["PrivateTest"]
    if not test_rows:
        # Some CSV re-uploads only have a single "Training"/"Test" split
        train_rows, test_rows = train_test_split(
            rows_by_usage["Training"], test_size=0.15, random_state=SEED
        )
        train_rows, val_rows = train_test_split(
            train_rows, test_size=VAL_SPLIT, random_state=SEED
        )

    write_rows(train_rows, TRAIN_DIR)
    write_rows(val_rows, VAL_DIR)
    write_rows(test_rows, TEST_DIR)
    print("Done. Wrote:", TRAIN_DIR, VAL_DIR, TEST_DIR)


def find_folder_layout() -> dict | None:
    """
    Detect a raw/<split>/<class>/*.jpg layout and return which split
    directories were found, e.g. {"train": "...", "test": "..."}.
    """
    if not os.path.isdir(RAW_DATA_DIR):
        return None
    found = {}
    for name in os.listdir(RAW_DATA_DIR):
        full = os.path.join(RAW_DATA_DIR, name)
        if not os.path.isdir(full):
            continue
        lname = name.lower()
        if lname in ("train", "training"):
            found["train"] = full
        elif lname in ("val", "validation", "valid"):
            found["validation"] = full
        elif lname in ("test", "testing"):
            found["test"] = full
    return found or None


def copy_class_folders(src_dir: str, dst_dir: str) -> None:
    ensure_dir(dst_dir)
    for class_name in sorted(os.listdir(src_dir)):
        src_class_dir = os.path.join(src_dir, class_name)
        if not os.path.isdir(src_class_dir):
            continue
        dst_class_dir = os.path.join(dst_dir, class_name)
        ensure_dir(dst_class_dir)
        for fname in os.listdir(src_class_dir):
            shutil.copy2(os.path.join(src_class_dir, fname), os.path.join(dst_class_dir, fname))


def preprocess_from_folders(layout: dict) -> None:
    print(f"Found folder-based dataset: {layout}")

    if "train" not in layout:
        fail("Could not find a 'train' folder inside data/raw/.")

    if "validation" in layout:
        copy_class_folders(layout["train"], TRAIN_DIR)
        copy_class_folders(layout["validation"], VAL_DIR)
    else:
        # Carve a validation split out of train
        print("No validation folder found — splitting one out of train "
              f"({VAL_SPLIT:.0%}).")
        ensure_dir(TRAIN_DIR)
        ensure_dir(VAL_DIR)
        for class_name in sorted(os.listdir(layout["train"])):
            src_class_dir = os.path.join(layout["train"], class_name)
            if not os.path.isdir(src_class_dir):
                continue
            files = os.listdir(src_class_dir)
            train_files, val_files = train_test_split(
                files, test_size=VAL_SPLIT, random_state=SEED
            )
            ensure_dir(os.path.join(TRAIN_DIR, class_name))
            ensure_dir(os.path.join(VAL_DIR, class_name))
            for fname in train_files:
                shutil.copy2(os.path.join(src_class_dir, fname),
                             os.path.join(TRAIN_DIR, class_name, fname))
            for fname in val_files:
                shutil.copy2(os.path.join(src_class_dir, fname),
                             os.path.join(VAL_DIR, class_name, fname))

    if "test" in layout:
        copy_class_folders(layout["test"], TEST_DIR)
    else:
        fail("Could not find a 'test' folder inside data/raw/. "
             "Add one, or split part of train/ into data/test manually.")

    print("Done. Wrote:", TRAIN_DIR, VAL_DIR, TEST_DIR)


def main() -> None:
    if os.path.isdir(TRAIN_DIR) and os.path.isdir(VAL_DIR) and os.path.isdir(TEST_DIR):
        print("data/train, data/validation, and data/test already exist — "
              "nothing to do. Delete them first if you want to re-run "
              "preprocessing from data/raw.")
        return

    csv_path = find_csv()
    if csv_path:
        preprocess_from_csv(csv_path)
        return

    layout = find_folder_layout()
    if layout:
        preprocess_from_folders(layout)
        return

    fail(
        "No dataset found in data/raw/. Download a facial-expression "
        "dataset from Kaggle and unzip it into data/raw/ first — either a "
        "fer2013.csv file, or train/<emotion>/*.jpg style folders. "
        "See the README's 'Dataset' section."
    )


if __name__ == "__main__":
    main()
