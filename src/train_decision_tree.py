"""Fold-local preprocessing + Decision Tree search on existing Train only."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import tempfile
from pathlib import Path

import joblib
import numpy as np
import scipy
import sklearn
from sklearn.base import clone
from sklearn.metrics import f1_score, make_scorer
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier

from .config import POSITIVE_LABEL, RANDOM_STATE, TARGET_COLUMN
from .duc_preprocessing import TelcoPreprocessor
from .evaluate import danh_gia_mo_hinh
from .feature_engineering_b import read_raw_csv, main as export_b

ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT / "data" / "processed"
MODELS_DIR = ROOT / "models"
RESULTS_DIR = ROOT / "results"
REPORT_DIR = ROOT / "report"
PARAM_GRID = {
    "tree__criterion": ["gini", "entropy"],
    "tree__max_depth": [3, 4, 5, 6, 8, None],
    "tree__min_samples_leaf": [1, 5, 10, 20, 40],
    "tree__class_weight": [None, "balanced"],
}


def load_numeric_matrix(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader, [])
        if not header or len(set(header)) != len(header):
            raise ValueError(f"Missing/duplicate header: {path}")
        rows = list(reader)
    if not rows or any(len(row) != len(header) for row in rows):
        raise ValueError(f"Empty or ragged matrix: {path}")
    matrix = np.asarray(rows, dtype=float)
    if not np.isfinite(matrix).all():
        raise ValueError(f"Missing/infinite matrix value: {path}")
    return matrix, header


def load_target(path):
    rows, fields = read_raw_csv(path)
    if fields != [TARGET_COLUMN]:
        raise ValueError(f"Expected a single {TARGET_COLUMN} column: {path}")
    values = np.asarray([row[TARGET_COLUMN] for row in rows], dtype=object)
    if set(values) != {"No", "Yes"}:
        raise ValueError(f"Expected No/Yes labels: {path}")
    return values


def make_cv():
    return StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)


def tune_decision_tree(X_train_raw, y_train, flow="B", n_jobs=2, param_grid=None):
    """No Test argument: each cloned pipeline fits only its training fold."""
    if len(X_train_raw) != len(y_train):
        raise ValueError("Train X/y length mismatch.")
    with tempfile.TemporaryDirectory(prefix="duc-cv-") as cache:
        pipeline = Pipeline([
            ("preprocess", TelcoPreprocessor(flow)),
            ("tree", DecisionTreeClassifier(random_state=RANDOM_STATE)),
        ], memory=joblib.Memory(cache, verbose=0))
        search = GridSearchCV(
            pipeline, PARAM_GRID if param_grid is None else param_grid,
            scoring=make_scorer(f1_score, pos_label=POSITIVE_LABEL, zero_division=0),
            cv=make_cv(), n_jobs=n_jobs, pre_dispatch=n_jobs if n_jobs > 0 else "2*n_jobs",
            refit=True, error_score="raise", return_train_score=False,
        )
        search.fit(X_train_raw, y_train)
        search.best_estimator_.memory = None
        search.estimator.memory = None
    return search


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")


def save_cv(path, search):
    keys = ["rank_test_score", "mean_test_score", "std_test_score"]
    keys += [f"split{i}_test_score" for i in range(5)]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["params"] + keys)
        writer.writeheader()
        for i, params in enumerate(search.cv_results_["params"]):
            writer.writerow({"params": json.dumps(params, sort_keys=True),
                             **{key: search.cv_results_[key][i] for key in keys}})


def best_params(search):
    return {key.removeprefix("tree__"): value for key, value in search.best_params_.items()}


def main(n_jobs=2):
    train, train_columns = read_raw_csv(PROCESSED_DIR / "X_train_raw.csv")
    y_train = load_target(PROCESSED_DIR / "y_train.csv")
    if len(train) != len(y_train):
        raise ValueError("Train X/y length mismatch.")
    # Both final flows are fixed. B_core documents the interactions' contribution;
    # its score does NOT change the final feature set after Test was inspected.
    searches = {}
    for flow in ("A", "B_core", "B"):
        print(f"GridSearchCV {flow}: Train only, 120 candidates x 5 folds", flush=True)
        searches[flow] = tune_decision_tree(train, y_train, flow, n_jobs)
        save_cv(REPORT_DIR / f"duc_cv_{flow}.csv", searches[flow])
        print(f"{flow} CV F1: {searches[flow].best_score_:.6f}", flush=True)
    comparison = [{"flow": flow, "features": len(s.best_estimator_["preprocess"].feature_names_),
                   "cv_f1": float(s.best_score_), "best_params": best_params(s)}
                  for flow, s in searches.items()]
    save_json(REPORT_DIR / "duc_feature_comparison.json", {"train_only": True, "rows": comparison})

    # No Test data are read until every search has finished.
    test, test_columns = read_raw_csv(PROCESSED_DIR / "X_test_raw.csv")
    y_test = load_target(PROCESSED_DIR / "y_test.csv")
    if train_columns != test_columns or len(test) != len(y_test):
        raise ValueError("Test schema/label length mismatch.")
    export_b()
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    versions = {"python": platform.python_version(), "scikit_learn": sklearn.__version__,
                "numpy": np.__version__, "scipy": scipy.__version__, "joblib": joblib.__version__}
    for flow in ("A", "B"):
        search = searches[flow]
        pipeline = search.best_estimator_
        transformer = pipeline["preprocess"]
        matrices = {}
        for split, rows in (("train", train), ("test", test)):
            matrix, columns = load_numeric_matrix(PROCESSED_DIR / f"X_{split}_{flow}.csv")
            if columns != transformer.feature_names_:
                raise ValueError(f"Unexpected feature names: {flow}/{split}")
            expected = transformer.transform(rows)
            if expected.shape != matrix.shape:
                raise ValueError(f"Matrix shape mismatch: {flow}/{split}")
            # Detect shuffled matrices as well as incompatible preprocessing.
            np.testing.assert_allclose(matrix, expected, rtol=1e-10, atol=1e-10)
            matrices[split] = matrix
        # Final refit uses the group's exact CSV values after recipe verification.
        tree = clone(pipeline["tree"]).fit(matrices["train"], y_train)
        predictions = tree.predict(matrices["test"])
        pipeline.steps[-1] = ("tree", tree)
        np.testing.assert_array_equal(pipeline.predict(test), predictions)
        metrics = danh_gia_mo_hinh(y_test, predictions, pos_label=POSITIVE_LABEL, in_chi_tiet=False)
        result = {"model_id": f"decision_tree_{flow}", "member": "Đức",
                  "model": "Decision Tree", "flow": flow, **metrics,
                  "confusion_matrix_labels": ["No", "Yes"],
                  "cv_scoring": "f1 (Churn=Yes), fold-local preprocessing",
                  "cv_best_f1": float(search.best_score_), "best_params": best_params(search),
                  "feature_count": len(transformer.feature_names_), "versions": versions}
        save_json(RESULTS_DIR / f"duc_decision_tree_{flow}.json", result)
        joblib.dump(tree, MODELS_DIR / f"decision_tree_{flow}.pkl")
        joblib.dump(pipeline, MODELS_DIR / f"decision_tree_{flow}_pipeline.pkl")
        with (REPORT_DIR / f"duc_predictions_{flow}.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["test_row", "y_true", "y_pred"])
            writer.writerows(zip(range(len(test)), y_test, predictions))
        print(json.dumps(result, ensure_ascii=True), flush=True)
    files = [f"data/processed/{name}.csv" for name in (
        "X_train_raw", "X_test_raw", "y_train", "y_test", "X_train_A", "X_test_A", "X_train_B", "X_test_B")]
    manifest = {"versions": versions, "random_state": RANDOM_STATE, "cv_folds": 5,
                "sha256": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in files},
                "test_history": "Test was inspected during earlier exploratory runs; not an untouched holdout.",
                "feature_policy": "B's 29 features fixed before this correction; no Test-driven retuning."}
    save_json(REPORT_DIR / "duc_run_manifest.json", manifest)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--jobs", type=int, default=2)
    args = parser.parse_args()
    main(n_jobs=args.jobs)
