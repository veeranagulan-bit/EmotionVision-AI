"""
ml/evaluate.py

Loads the trained model and produces real evaluation artifacts from the
test set: accuracy, precision/recall/F1 per class, a full classification
report, and a confusion matrix image. Nothing here is fabricated — every
number comes from running the saved model against data/test.

Run after ml/train.py:
    python ml/evaluate.py
"""

import os
import sys

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import tensorflow as tf
from sklearn.metrics import (
    classification_report, confusion_matrix, precision_recall_fscore_support,
)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import (  # noqa: E402
    MODEL_PATH, LABELS_PATH, TEST_DIR, IMAGE_SIZE, BATCH_SIZE,
    CONFUSION_MATRIX_PATH, METRICS_PATH,
)
from utils import load_json, save_json, ensure_dir, fail  # noqa: E402


def main() -> None:
    if not os.path.exists(MODEL_PATH):
        fail(f"No trained model found at {MODEL_PATH}. Run `python ml/train.py` first.")
    if not os.path.isdir(TEST_DIR):
        fail(f"Test set not found at {TEST_DIR}. See README 'Dataset' section.")

    print(f"Loading model from {MODEL_PATH}")
    model = tf.keras.models.load_model(MODEL_PATH)

    labels_data = load_json(LABELS_PATH)
    class_names = labels_data["labels"]

    test_ds = tf.keras.utils.image_dataset_from_directory(
        TEST_DIR, image_size=IMAGE_SIZE, batch_size=BATCH_SIZE,
        label_mode="categorical", shuffle=False,
    )
    # Ensure the test set's own folder-derived class order matches the
    # model's training-time label order before comparing predictions.
    if test_ds.class_names != class_names:
        fail(
            "Test set class folders do not match the labels the model was "
            f"trained on.\n  Model labels: {class_names}\n  Test folders: "
            f"{test_ds.class_names}\nRe-run preprocessing so all three "
            "splits share identical class folders."
        )

    print("Running predictions on the test set...")
    y_true, y_pred = [], []
    for images, labels in test_ds:
        preds = model.predict(images, verbose=0)
        y_true.extend(np.argmax(labels.numpy(), axis=1))
        y_pred.extend(np.argmax(preds, axis=1))

    y_true, y_pred = np.array(y_true), np.array(y_pred)

    report_dict = classification_report(
        y_true, y_pred, target_names=class_names, output_dict=True, zero_division=0
    )
    report_text = classification_report(
        y_true, y_pred, target_names=class_names, zero_division=0
    )
    print("\nClassification report:\n")
    print(report_text)

    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, average=None, zero_division=0
    )
    overall_accuracy = float((y_true == y_pred).mean())
    print(f"Overall test accuracy: {overall_accuracy:.4f}")

    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots(figsize=(7, 6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="mako", xticklabels=class_names,
                yticklabels=class_names, ax=ax)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_title("Confusion Matrix (test set)")
    fig.tight_layout()
    ensure_dir(os.path.dirname(CONFUSION_MATRIX_PATH))
    fig.savefig(CONFUSION_MATRIX_PATH, dpi=150)
    plt.close(fig)
    print(f"Saved confusion matrix to {CONFUSION_MATRIX_PATH}")

    # Merge into the metrics.json the training script already wrote, so the
    # frontend's "Model" page can show a single, complete, real metrics file.
    existing_metrics = load_json(METRICS_PATH) if os.path.exists(METRICS_PATH) else {}
    existing_metrics.update({
        "overall_test_accuracy": overall_accuracy,
        "per_class": {
            class_names[i]: {
                "precision": float(precision[i]),
                "recall": float(recall[i]),
                "f1_score": float(f1[i]),
                "support": int(support[i]),
            }
            for i in range(len(class_names))
        },
        "macro_avg": report_dict["macro avg"],
        "weighted_avg": report_dict["weighted avg"],
    })
    save_json(existing_metrics, METRICS_PATH)
    print(f"Updated {METRICS_PATH} with full evaluation results.")


if __name__ == "__main__":
    main()
