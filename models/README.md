# Models

This directory is where `ml/train.py` and `ml/evaluate.py` write their
output. The large trained-model binary is intentionally excluded from
version control (see the root `.gitignore`) — everything else here is
small enough to commit and is kept in the repo as real, generated evidence
of how the model performs.

## Generated here after training

| File | Produced by | Committed to git? |
|---|---|---|
| `emotion_model.keras` | `ml/train.py` | No (too large — see below) |
| `checkpoints/best_model.keras` | `ml/train.py` (mid-training) | No |
| `labels.json` | `ml/train.py` | Yes |
| `metrics.json` | `ml/train.py`, extended by `ml/evaluate.py` | Yes |
| `class_distribution.png` | `ml/dataset.py` | Yes |
| `training_history.png` | `ml/train.py` | Yes |
| `confusion_matrix.png` | `ml/evaluate.py` | Yes |

## How to get a trained model

You have two options:

1. **Train it yourself** (recommended — see the root README's "Training"
   section):

   ```bash
   python ml/train.py
   python ml/evaluate.py
   ```

   On a laptop CPU this takes roughly 30–90 minutes depending on dataset
   size and backbone; a GPU brings it down to a few minutes.

2. **Download a pre-trained model** if the maintainer has published one
   (e.g. as a GitHub Release asset, since GitHub blocks large files in
   normal commits). Place it at `models/emotion_model.keras` and the
   matching `models/labels.json` next to it.

## Why the model isn't committed directly

Trained Keras models for this architecture are typically tens of megabytes,
which is workable but still poor practice to commit directly and impossible
once a project accumulates several versions. If you want to publish yours:

- **GitHub Releases** — attach `emotion_model.keras` as a release asset and
  link it from the main README.
- **Git LFS** — if you'd rather keep it in the repo history.
- **Cloud storage** (S3 / GCS / Hugging Face Hub) — download it as a
  post-install step in your deployment pipeline.

Until a trained model is present, the backend's `/health` endpoint reports
`"model_loaded": false` and `/predict` returns a `503` with a clear message
instead of a fabricated prediction.
