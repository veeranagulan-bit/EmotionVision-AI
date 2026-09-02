# Dataset

This project does not redistribute the Kaggle dataset. Download it yourself
and place it here.

## Option A — FER-2013 (recommended, matches the default label set)

1. Go to Kaggle and search for **"FER-2013"** or **"Facial Expression
   Recognition 2013"** (e.g. `msambare/fer2013` or the original
   `deadskull7/fer2013` CSV upload — either works, see below).
2. Download the dataset (you'll need a free Kaggle account, and either the
   Kaggle CLI or the website's Download button).
3. Unzip it into `data/raw/` so this directory contains either:
   - `data/raw/fer2013.csv` (the classic CSV format), **or**
   - `data/raw/train/<emotion>/*.jpg` and `data/raw/test/<emotion>/*.jpg`
     (the folder-of-images format some re-uploads use).
4. From the project root, run:

   ```bash
   python ml/preprocess.py
   ```

   This detects which format you downloaded and writes the standardized
   structure below.

## Option B — Kaggle CLI

```bash
pip install kaggle
# place your kaggle.json API token in ~/.kaggle/ first
kaggle datasets download -d msambare/fer2013 -p data/raw --unzip
python ml/preprocess.py
```

## Option C — a different Kaggle facial-expression dataset

`ml/preprocess.py` and `ml/dataset.py` never hard-code class names — they
read whatever class folders are actually present. If your dataset already
looks like the target structure below, you can skip `preprocess.py`
entirely and just place it directly at `data/train`, `data/validation`,
`data/test`.

## Target structure (what `ml/preprocess.py` produces)

```text
data/
├── train/
│   ├── Angry/
│   ├── Disgust/
│   ├── Fear/
│   ├── Happy/
│   ├── Neutral/
│   ├── Sad/
│   └── Surprise/
├── validation/
│   └── ... (same class folders)
└── test/
    └── ... (same class folders)
```

Once this exists, run `python ml/dataset.py` to inspect the real class
distribution, image dimensions, and check for corrupted files before
training.
