"""
ml/train.py

Trains the emotion-classification model using transfer learning:

    1. Load a pretrained backbone (MobileNetV3 / EfficientNetB0 / ResNet50)
       with ImageNet weights, frozen.
    2. Attach a small classification head and train only the head.
    3. Unfreeze the top N backbone layers and fine-tune at a low learning
       rate.
    4. Evaluate on the test set and save real metrics (never fabricated).
    5. Save the trained model, the label list, and the metrics to models/.

Run:
    python ml/train.py

Requires the dataset to already be prepared under data/train, data/validation,
data/test (see ml/preprocess.py / README "Dataset" section).
"""

import json
import os
import sys
import time

import tensorflow as tf
from tensorflow.keras import layers, models

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import (  # noqa: E402
    BACKBONE, IMAGE_SIZE, MODEL_PATH, BEST_CHECKPOINT_PATH, LABELS_PATH,
    METRICS_PATH, TRAINING_HISTORY_PATH, EPOCHS_HEAD, EPOCHS_FINE_TUNE,
    LEARNING_RATE_HEAD, LEARNING_RATE_FINE_TUNE, FINE_TUNE_UNFREEZE_LAYERS,
    EARLY_STOPPING_PATIENCE, REDUCE_LR_PATIENCE, REDUCE_LR_FACTOR,
    USE_CLASS_WEIGHTS, TRAIN_DIR,
)
from dataset import build_datasets, get_class_distribution, compute_class_weights  # noqa: E402
from utils import ensure_dir, save_json  # noqa: E402

import matplotlib.pyplot as plt


BACKBONE_BUILDERS = {
    "mobilenetv3": lambda input_shape: tf.keras.applications.MobileNetV3Large(
        input_shape=input_shape, include_top=False, weights="imagenet",
    ),
    "efficientnetb0": lambda input_shape: tf.keras.applications.EfficientNetB0(
        input_shape=input_shape, include_top=False, weights="imagenet",
    ),
    "resnet50": lambda input_shape: tf.keras.applications.ResNet50(
        input_shape=input_shape, include_top=False, weights="imagenet",
    ),
}

PREPROCESS_FNS = {
    "mobilenetv3": tf.keras.applications.mobilenet_v3.preprocess_input,
    "efficientnetb0": tf.keras.applications.efficientnet.preprocess_input,
    "resnet50": tf.keras.applications.resnet50.preprocess_input,
}


def build_model(num_classes: int) -> tuple[tf.keras.Model, tf.keras.Model]:
    input_shape = IMAGE_SIZE + (3,)
    inputs = layers.Input(shape=input_shape)

    preprocess = PREPROCESS_FNS[BACKBONE]
    x = layers.Lambda(preprocess, name="preprocess")(inputs)

    backbone = BACKBONE_BUILDERS[BACKBONE](input_shape)
    backbone.trainable = False
    x = backbone(x, training=False)

    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.3)(x)
    x = layers.Dense(256, activation="relu")(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(num_classes, activation="softmax", name="predictions")(x)

    model = models.Model(inputs, outputs, name=f"emotionvision_{BACKBONE}")
    return model, backbone


def compile_model(model: tf.keras.Model, lr: float) -> None:
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=lr),
        loss="categorical_crossentropy",
        metrics=["accuracy", tf.keras.metrics.AUC(name="auc")],
    )


def get_callbacks() -> list:
    ensure_dir(os.path.dirname(BEST_CHECKPOINT_PATH))
    return [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss", patience=EARLY_STOPPING_PATIENCE, restore_best_weights=True
        ),
        tf.keras.callbacks.ModelCheckpoint(
            BEST_CHECKPOINT_PATH, monitor="val_accuracy", save_best_only=True
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=REDUCE_LR_FACTOR, patience=REDUCE_LR_PATIENCE, min_lr=1e-7
        ),
    ]


def plot_history(history_head, history_fine, save_path: str) -> None:
    acc = history_head.history["accuracy"] + history_fine.history["accuracy"]
    val_acc = history_head.history["val_accuracy"] + history_fine.history["val_accuracy"]
    loss = history_head.history["loss"] + history_fine.history["loss"]
    val_loss = history_head.history["val_loss"] + history_fine.history["val_loss"]
    split_epoch = len(history_head.history["accuracy"])

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    axes[0].plot(acc, label="train")
    axes[0].plot(val_acc, label="validation")
    axes[0].axvline(split_epoch, color="gray", linestyle="--", label="fine-tune start")
    axes[0].set_title("Accuracy")
    axes[0].set_xlabel("Epoch")
    axes[0].legend()

    axes[1].plot(loss, label="train")
    axes[1].plot(val_loss, label="validation")
    axes[1].axvline(split_epoch, color="gray", linestyle="--", label="fine-tune start")
    axes[1].set_title("Loss")
    axes[1].set_xlabel("Epoch")
    axes[1].legend()

    fig.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)
    print(f"Saved training curves to {save_path}")


def main() -> None:
    print(f"Backbone: {BACKBONE}")
    print("Building datasets...")
    train_ds, val_ds, test_ds, class_names = build_datasets()
    num_classes = len(class_names)
    print(f"Classes ({num_classes}): {class_names}")

    class_weights = None
    if USE_CLASS_WEIGHTS:
        counts = get_class_distribution(TRAIN_DIR)
        class_weights = compute_class_weights(counts, class_names)
        print(f"Using class weights (imbalance correction): {class_weights}")

    model, backbone = build_model(num_classes)
    compile_model(model, LEARNING_RATE_HEAD)
    model.summary()

    print(f"\n=== Phase 1: training classification head ({EPOCHS_HEAD} epochs) ===")
    start = time.time()
    history_head = model.fit(
        train_ds, validation_data=val_ds, epochs=EPOCHS_HEAD,
        callbacks=get_callbacks(), class_weight=class_weights,
    )
    print(f"Head training took {time.time() - start:.1f}s")

    print(f"\n=== Phase 2: fine-tuning top {FINE_TUNE_UNFREEZE_LAYERS} backbone layers "
          f"({EPOCHS_FINE_TUNE} epochs) ===")
    backbone.trainable = True
    for layer in backbone.layers[:-FINE_TUNE_UNFREEZE_LAYERS]:
        layer.trainable = False
    compile_model(model, LEARNING_RATE_FINE_TUNE)

    start = time.time()
    history_fine = model.fit(
        train_ds, validation_data=val_ds, epochs=EPOCHS_FINE_TUNE,
        callbacks=get_callbacks(), class_weight=class_weights,
    )
    print(f"Fine-tuning took {time.time() - start:.1f}s")

    plot_history(history_head, history_fine, TRAINING_HISTORY_PATH)

    print("\n=== Evaluating on test set ===")
    test_loss, test_acc, test_auc = model.evaluate(test_ds)
    print(f"Test accuracy: {test_acc:.4f}  |  Test loss: {test_loss:.4f}  |  Test AUC: {test_auc:.4f}")

    ensure_dir(os.path.dirname(MODEL_PATH))
    model.save(MODEL_PATH)
    print(f"Saved trained model to {MODEL_PATH}")

    save_json({"labels": class_names}, LABELS_PATH)
    print(f"Saved label list to {LABELS_PATH}")

    # Store the metrics that were ACTUALLY measured — the backend and
    # frontend "Model" page read this file rather than any invented numbers.
    summary_metrics = {
        "backbone": BACKBONE,
        "num_classes": num_classes,
        "classes": class_names,
        "final_train_accuracy": float(history_fine.history["accuracy"][-1]),
        "final_val_accuracy": float(history_fine.history["val_accuracy"][-1]),
        "test_accuracy": float(test_acc),
        "test_loss": float(test_loss),
        "test_auc": float(test_auc),
        "epochs_head": len(history_head.history["accuracy"]),
        "epochs_fine_tune": len(history_fine.history["accuracy"]),
    }
    save_json(summary_metrics, METRICS_PATH)
    print(f"Saved metrics summary to {METRICS_PATH}")
    print("\nNext step: run `python ml/evaluate.py` for a full classification "
          "report, per-class precision/recall/F1, and a confusion matrix.")


if __name__ == "__main__":
    main()
