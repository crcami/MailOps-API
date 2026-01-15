"""Train and persist a local intent classifier."""
from __future__ import annotations

import json
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "intent_samples.jsonl"
MODEL_PATH = ROOT / "models" / "intent_classifier.joblib"

_ALLOWED_LABELS = {"PRAISE", "RESUME", "COMPLAINT", "SUPPORT", "OTHER"}


def main() -> None:
    """Train a multiclass classifier and save it."""
    texts, labels = _load_data(DATA_PATH)
    _validate_labels(labels)

    pipeline = Pipeline(
        steps=[
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_df=0.95)),
            ("clf", LogisticRegression(max_iter=1200, class_weight="balanced")),
        ]
    )

    pipeline.fit(texts, labels)

    bundle = {
        "pipeline": pipeline,
        "labels": list(getattr(pipeline.named_steps["clf"], "classes_", sorted(set(labels)))),
    }

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, MODEL_PATH)

    print(f"Saved model to: {MODEL_PATH}")
    print(f"Labels: {bundle['labels']}")


def _load_data(path: Path) -> tuple[list[str], list[str]]:
    """Load JSONL dataset."""
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    texts: list[str] = []
    labels: list[str] = []

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            texts.append(str(obj["text"]))
            labels.append(str(obj["label"]))

    if not texts:
        raise ValueError("Dataset is empty.")

    return texts, labels


def _validate_labels(labels: list[str]) -> None:
    """Validate that labels are allowed."""
    invalid = sorted({lbl for lbl in labels if lbl not in _ALLOWED_LABELS})
    if invalid:
        raise ValueError(f"Invalid labels found: {invalid}")


if __name__ == "__main__":
    main()
