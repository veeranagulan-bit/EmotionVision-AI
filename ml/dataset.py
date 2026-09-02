"""
ml/dataset.py

Loads the prepared train/validation/test folders as tf.data pipelines,
and provides inspection utilities: class list, class distribution, image
dimension check, and a basic corrupted-image scan.

Nothing about the dataset's class names or class count is hard-coded here —
everything is derived from the folder names actually present under
config.TRAIN_DIR.
"""

import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from PIL import Image, UnidentifiedImageError

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import (  # noqa: E402
    TRAIN_DIR, VAL_DIR, TEST_DIR, IMAGE_SIZE, BATCH_SIZE, SEED,
    AUGMENTATION, CLASS_DISTRIBUTION_PATH,
)
from utils import check_dataset_present, ensure_dir  # noqa: E402


def get_class_names() -> list[str]:
    """Read the true class names from the training folder's subdirectories."""
    check_dataset_present(TRAIN_DIR, VAL_DIR, TEST_DIR)
    classes = sorted(
        d for d in os.listdir(TRAIN_DIR) if os.path.isdir(os.path.join(TRAIN_DIR, d))
    )
    if not classes:
        raise RuntimeError(f"No class subfolders found under {TRAIN_DIR}")
    return classes


def get_class_distribution(split_dir: str) -> dict[str, int]:
    """Count images per class in a given split directory."""
    counts = {}
    for class_name in sorted(os.listdir(split_dir)):
        class_dir = os.path.join(split_dir, class_name)
        if not os.path.isdir(class_dir):
            continue
        counts[class_name] = len([
            f for f in os.listdir(class_dir)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ])
    return counts


def plot_class_distribution(save_path: str = CLASS_DISTRIBUTION_PATH) -> dict[str, int]:
    """Plot and save the real class distribution of the training set."""
    counts = get_class_distribution(TRAIN_DIR)
    ensure_dir(os.path.dirname(save_path))

    fig, ax = plt.subplots(figsize=(9, 5))
    classes = list(counts.keys())
    values = list(counts.values())
    ax.bar(classes, values, color="#8B7FFF")
    ax.set_title("Training Set — Class Distribution (actual counts)")
    ax.set_ylabel("Number of images")
    ax.set_xlabel("Emotion class")
    for i, v in enumerate(values):
        ax.text(i, v, str(v), ha="center", va="bottom", fontsize=9)
    fig.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)
    print(f"Saved class distribution chart to {save_path}")
    return counts


def compute_class_weights(counts: dict[str, int], class_names: list[str]) -> dict[int, float]:
    """Inverse-frequency class weights, used to counter class imbalance
    (e.g. FER-2013's 'Disgust' class has far fewer samples than the rest)."""
    total = sum(counts.values())
    n_classes = len(class_names)
    weights = {}
    for i, name in enumerate(class_names):
        count = max(counts.get(name, 0), 1)
        weights[i] = total / (n_classes * count)
    return weights


def scan_for_corrupted_images(split_dir: str) -> list[str]:
    """Attempt to open every image in a split; return paths that fail to load."""
    bad = []
    for class_name in os.listdir(split_dir):
        class_dir = os.path.join(split_dir, class_name)
        if not os.path.isdir(class_dir):
            continue
        for fname in os.listdir(class_dir):
            fpath = os.path.join(class_dir, fname)
            try:
                with Image.open(fpath) as img:
                    img.verify()
            except (UnidentifiedImageError, OSError):
                bad.append(fpath)
    return bad


def inspect_image_dimensions(split_dir: str, sample_size: int = 200) -> dict:
    """Sample a handful of images and report the range of dimensions found."""
    sizes = []
    count = 0
    for class_name in os.listdir(split_dir):
        class_dir = os.path.join(split_dir, class_name)
        if not os.path.isdir(class_dir):
            continue
        for fname in os.listdir(class_dir):
            if count >= sample_size:
                break
            try:
                with Image.open(os.path.join(class_dir, fname)) as img:
                    sizes.append(img.size)
                count += 1
            except Exception:
                continue
    if not sizes:
        return {}
    widths, heights = zip(*sizes)
    return {
        "sampled": len(sizes),
        "min_width": min(widths), "max_width": max(widths),
        "min_height": min(heights), "max_height": max(heights),
    }


def _augmentation_layers() -> tf.keras.Sequential:
    """
    Light, realistic augmentation only — deliberately avoids extreme
    transforms (large rotations, heavy shear, aggressive color jitter) that
    would distort or invert the facial expression itself.
    """
    cfg = AUGMENTATION
    layers = [tf.keras.layers.RandomFlip("horizontal")] if cfg["horizontal_flip"] else []
    layers += [
        tf.keras.layers.RandomRotation(cfg["rotation_range"] / 360.0, seed=SEED),
        tf.keras.layers.RandomZoom(cfg["zoom_range"], seed=SEED),
        tf.keras.layers.RandomTranslation(
            cfg["height_shift_range"], cfg["width_shift_range"], seed=SEED
        ),
        tf.keras.layers.RandomBrightness(
            factor=(cfg["brightness_range"][0] - 1, cfg["brightness_range"][1] - 1),
            seed=SEED,
        ),
    ]
    return tf.keras.Sequential(layers, name="augmentation")


def build_datasets():
    """
    Returns (train_ds, val_ds, test_ds, class_names) as batched, prefetched
    tf.data.Dataset objects. Augmentation is applied only to the training set.
    """
    check_dataset_present(TRAIN_DIR, VAL_DIR, TEST_DIR)

    train_ds = tf.keras.utils.image_dataset_from_directory(
        TRAIN_DIR, image_size=IMAGE_SIZE, batch_size=BATCH_SIZE,
        label_mode="categorical", seed=SEED, shuffle=True,
    )
    class_names = train_ds.class_names

    val_ds = tf.keras.utils.image_dataset_from_directory(
        VAL_DIR, image_size=IMAGE_SIZE, batch_size=BATCH_SIZE,
        label_mode="categorical", seed=SEED, shuffle=False,
    )
    test_ds = tf.keras.utils.image_dataset_from_directory(
        TEST_DIR, image_size=IMAGE_SIZE, batch_size=BATCH_SIZE,
        label_mode="categorical", seed=SEED, shuffle=False,
    )

    augment = _augmentation_layers()
    train_ds = train_ds.map(
        lambda x, y: (augment(x, training=True), y),
        num_parallel_calls=tf.data.AUTOTUNE,
    )

    train_ds = train_ds.prefetch(tf.data.AUTOTUNE)
    val_ds = val_ds.prefetch(tf.data.AUTOTUNE)
    test_ds = test_ds.prefetch(tf.data.AUTOTUNE)

    return train_ds, val_ds, test_ds, class_names


if __name__ == "__main__":
    print("Inspecting dataset...\n")
    classes = get_class_names()
    print(f"Classes found ({len(classes)}): {classes}\n")

    print("Class distribution (train):")
    counts = plot_class_distribution()
    for k, v in counts.items():
        print(f"  {k:12s} {v}")

    print("\nSampling image dimensions (train)...")
    dims = inspect_image_dimensions(TRAIN_DIR)
    print(f"  {dims}")

    print("\nScanning for corrupted images (this can take a while on large datasets)...")
    bad = scan_for_corrupted_images(TRAIN_DIR)
    print(f"  Found {len(bad)} unreadable file(s)." if bad else "  No corrupted images found.")
    for b in bad[:20]:
        print(f"    {b}")
