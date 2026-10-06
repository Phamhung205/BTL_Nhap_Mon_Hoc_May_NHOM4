"""Export B from the existing split; never split, shuffle or drop rows."""
from __future__ import annotations

import csv
from pathlib import Path

import joblib
import numpy as np

# Always imported, even with -m: pickle never refers to __main__.FeatureEngineerB.
from .duc_preprocessing import FeatureEngineerB, NUMERIC, CATEGORICAL

ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT / "data" / "processed"
MODELS_DIR = ROOT / "models"


def read_raw_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames
        if not fields or len(fields) != len(set(fields)):
            raise ValueError(f"Missing/duplicate CSV header: {path}")
        rows = list(reader)
    if not rows or any(None in row or None in row.values() for row in rows):
        raise ValueError(f"Empty or ragged CSV: {path}")
    return rows, fields


def write_matrix_csv(path, feature_names, matrix):
    path = Path(path)
    matrix = np.asarray(matrix, dtype=float)
    if matrix.ndim != 2 or matrix.shape[1] != len(feature_names) or not np.isfinite(matrix).all():
        raise ValueError("Invalid output matrix.")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(feature_names)
        writer.writerows(matrix)


def build_flow_b(train_path=PROCESSED_DIR / "X_train_raw.csv",
                 test_path=PROCESSED_DIR / "X_test_raw.csv"):
    train, train_columns = read_raw_csv(train_path)
    test, test_columns = read_raw_csv(test_path)
    if train_columns != test_columns or set(train_columns) != set(NUMERIC + CATEGORICAL):
        raise ValueError("Unexpected raw schema or mismatched Train/Test columns.")
    transformer = FeatureEngineerB().fit(train)
    return transformer, transformer.transform(train), transformer.transform(test)


def main():
    from .train_decision_tree import load_target

    transformer, train, test = build_flow_b()
    for split, matrix in (("train", train), ("test", test)):
        if len(matrix) != len(load_target(PROCESSED_DIR / f"y_{split}.csv")):
            raise ValueError(f"X/y length mismatch: {split}")
    for split, matrix in (("train", train), ("test", test)):
        write_matrix_csv(PROCESSED_DIR / f"X_{split}_B.csv", transformer.feature_names_, matrix)
        print(f"X_{split}_B: {matrix.shape}")
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(transformer, MODELS_DIR / "feature_engineer_B.pkl")


if __name__ == "__main__":
    main()
