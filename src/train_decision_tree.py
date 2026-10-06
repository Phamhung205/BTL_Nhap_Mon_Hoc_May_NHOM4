"""Tinh chinh va danh gia Decision Tree tren Luong A va Luong B."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
from sklearn.metrics import f1_score, make_scorer
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.tree import DecisionTreeClassifier

from .config import POSITIVE_LABEL, RANDOM_STATE, TARGET_COLUMN
from .evaluate import danh_gia_mo_hinh


ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT / "data" / "processed"
MODELS_DIR = ROOT / "models"
RESULTS_DIR = ROOT / "results"


PARAM_GRID = {
    "criterion": ["gini", "entropy"],
    "max_depth": [3, 4, 5, 6, 8, None],
    "min_samples_leaf": [1, 5, 10, 20, 40],
    "class_weight": [None, "balanced"],
}


def load_numeric_matrix(path: Path) -> tuple[np.ndarray, list[str]]:
    """Doc ma tran CSV thuần số va kiem tra moi dong co du cot."""
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        try:
            header = next(reader)
        except StopIteration as exc:
            raise ValueError(f"{path} rong.") from exc

        rows: list[list[float]] = []
        for row_number, row in enumerate(reader, start=2):
            if len(row) != len(header):
                raise ValueError(
                    f"{path.name} dong {row_number}: {len(row)} cot, "
                    f"can {len(header)}."
                )
            rows.append([float(value) for value in row])

    matrix = np.asarray(rows, dtype=float)
    if matrix.ndim != 2 or matrix.shape[1] != len(header):
        raise ValueError(f"Ma tran {path.name} khong hop le.")
    if not np.isfinite(matrix).all():
        raise ValueError(f"{path.name} con gia tri thieu/vo han.")
    return matrix, header


def load_target(path: Path) -> np.ndarray:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or TARGET_COLUMN not in reader.fieldnames:
            raise ValueError(f"{path.name} thieu cot {TARGET_COLUMN}.")
        values = [row[TARGET_COLUMN] for row in reader]

    labels = np.asarray(values, dtype=object)
    if set(labels) != {"No", "Yes"}:
        raise ValueError(f"Nhan trong {path.name} khong dung No/Yes.")
    return labels


def tune_decision_tree(
    X_train: np.ndarray,
    y_train: np.ndarray,
) -> GridSearchCV:
    """Grid search chi tren Train, toi uu F1 cua lop Churn=Yes."""
    cv = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=RANDOM_STATE,
    )
    scorer = make_scorer(f1_score, pos_label=POSITIVE_LABEL)

    search = GridSearchCV(
        estimator=DecisionTreeClassifier(random_state=RANDOM_STATE),
        param_grid=PARAM_GRID,
        scoring=scorer,
        cv=cv,
        n_jobs=-1,
        refit=True,
        return_train_score=False,
    )
    search.fit(X_train, y_train)
    return search


def make_result(
    flow: str,
    metrics: dict[str, Any],
    search: GridSearchCV,
    feature_count: int,
) -> dict[str, Any]:
    return {
        "model_id": f"decision_tree_{flow}",
        "member": "Đức",
        "model": "Decision Tree",
        "flow": flow,
        "accuracy": metrics["accuracy"],
        "precision": metrics["precision"],
        "recall": metrics["recall"],
        "f1_score": metrics["f1_score"],
        "confusion_matrix": metrics["confusion_matrix"],
        "positive_label": POSITIVE_LABEL,
        "cv_scoring": "f1 (Churn=Yes)",
        "cv_best_f1": float(search.best_score_),
        "best_params": search.best_params_,
        "feature_count": feature_count,
    }


def save_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def train_and_evaluate_flow(
    flow: str,
    X_train: np.ndarray,
    X_test: np.ndarray,
    y_train: np.ndarray,
    y_test: np.ndarray,
) -> dict[str, Any]:
    if len(X_train) != len(y_train) or len(X_test) != len(y_test):
        raise AssertionError(f"Luong {flow}: so dong X/y khong khop.")
    if X_train.shape[1] != X_test.shape[1]:
        raise AssertionError(f"Luong {flow}: so cot Train/Test khong khop.")

    search = tune_decision_tree(X_train, y_train)
    predictions = search.predict(X_test)
    metrics = danh_gia_mo_hinh(
        y_test,
        predictions,
        pos_label=POSITIVE_LABEL,
        in_chi_tiet=False,
    )
    result = make_result(flow, metrics, search, X_train.shape[1])

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    model_path = MODELS_DIR / f"decision_tree_{flow}.pkl"
    result_path = RESULTS_DIR / f"duc_decision_tree_{flow}.json"
    joblib.dump(search.best_estimator_, model_path)
    save_json(result_path, result)

    print(f"\n===== DECISION TREE - LUONG {flow} =====")
    print(f"Best CV F1 : {search.best_score_:.6f}")
    print(f"Best params: {search.best_params_}")
    print(f"Accuracy   : {metrics['accuracy']:.6f}")
    print(f"Precision  : {metrics['precision']:.6f}")
    print(f"Recall     : {metrics['recall']:.6f}")
    print(f"F1-score   : {metrics['f1_score']:.6f}")
    print(f"CM [No,Yes]: {metrics['confusion_matrix']}")
    print(f"Da luu     : {result_path}")
    return result


def main() -> None:
    y_train = load_target(PROCESSED_DIR / "y_train.csv")
    y_test = load_target(PROCESSED_DIR / "y_test.csv")

    for flow in ("A", "B"):
        X_train, train_columns = load_numeric_matrix(
            PROCESSED_DIR / f"X_train_{flow}.csv"
        )
        X_test, test_columns = load_numeric_matrix(
            PROCESSED_DIR / f"X_test_{flow}.csv"
        )
        if train_columns != test_columns:
            raise AssertionError(f"Luong {flow}: ten/thu tu cot Train/Test khong khop.")
        train_and_evaluate_flow(
            flow,
            X_train,
            X_test,
            y_train,
            y_test,
        )


if __name__ == "__main__":
    main()
