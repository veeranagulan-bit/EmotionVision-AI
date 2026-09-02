"""Stub heavy tensorflow import for fast, GPU-free test runs.

In a real environment with tensorflow installed (per requirements.txt),
this stub is unnecessary and can be deleted — it exists so the test suite
can run quickly without requiring a full TensorFlow install just to check
routing/validation logic.
"""
import sys
from unittest.mock import MagicMock

if "tensorflow" not in sys.modules:
    try:
        import tensorflow  # noqa: F401
    except ImportError:
        sys.modules["tensorflow"] = MagicMock()
        sys.modules["tensorflow.keras"] = MagicMock()
