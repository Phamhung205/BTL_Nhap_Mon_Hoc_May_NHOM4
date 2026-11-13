"""Decision Tree trên Luồng A và Luồng B (phần của Đức).

Chạy từ thư mục gốc dự án:

    python -m src.feature_engineering_b     # tạo X_train_B.csv, X_test_B.csv
    python -m src.train_decision_tree

Với mỗi luồng:
1. Đọc X_train / X_test của luồng và nhãn do Mạnh chia (không chia lại).
2. GridSearchCV 5-fold CHỈ trên tập Train, chọn tham số theo F1 của lớp Churn = Yes.
3. Đánh giá mô hình tốt nhất trên tập Test chung, lưu JSON cho Hùng và lưu mô hình.
"""

import json
import sys
from pathlib import Path

import joblib
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import ConfusionMatrixDisplay, f1_score, make_scorer
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.tree import DecisionTreeClassifier, plot_tree

from .config import POSITIVE_LABEL, RANDOM_STATE, TARGET_COLUMN
from .evaluate import danh_gia_mo_hinh

ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT / "data" / "processed"
MODELS_DIR = ROOT / "models"
RESULTS_DIR = ROOT / "results"
FIGURES_DIR = ROOT / "report" / "figures"

PARAM_GRID = {
    "criterion": ["gini", "entropy"],
    "max_depth": [3, 4, 5, 6, 7, 8, 10, 12, None],
    "min_samples_leaf": [1, 5, 10, 20, 30, 50, 75, 100],
    "class_weight": [None, "balanced"],
}


def doc_du_lieu(luong):
    """Đọc dữ liệu của Luồng A hoặc B cùng nhãn Train/Test."""
    X_train = pd.read_csv(PROCESSED_DIR / f"X_train_{luong}.csv")
    X_test = pd.read_csv(PROCESSED_DIR / f"X_test_{luong}.csv")
    y_train = pd.read_csv(PROCESSED_DIR / "y_train.csv")[TARGET_COLUMN]
    y_test = pd.read_csv(PROCESSED_DIR / "y_test.csv")[TARGET_COLUMN]
    return X_train, X_test, y_train, y_test


def tim_tham_so(X_train, y_train):
    """GridSearchCV trên tập Train, tiêu chí F1-score của lớp Churn = Yes."""
    search = GridSearchCV(
        estimator=DecisionTreeClassifier(random_state=RANDOM_STATE),
        param_grid=PARAM_GRID,
        scoring=make_scorer(f1_score, pos_label=POSITIVE_LABEL),
        cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE),
        n_jobs=-1,
    )
    search.fit(X_train, y_train)
    return search


def luu_ket_qua(luong, search, metrics):
    """Lưu JSON (theo results/result_template.json) và mô hình."""
    result = {
        "model_id": f"decision_tree_{luong}",
        "member": "Đức",
        "model": "Decision Tree",
        "flow": luong,
        "accuracy": metrics["accuracy"],
        "precision": metrics["precision"],
        "recall": metrics["recall"],
        "f1_score": metrics["f1_score"],
        "confusion_matrix": metrics["confusion_matrix"],
        "best_params": search.best_params_,
        "cv_f1": search.best_score_,
    }
    with open(RESULTS_DIR / f"duc_decision_tree_{luong}.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    MODELS_DIR.mkdir(exist_ok=True)
    joblib.dump(search.best_estimator_, MODELS_DIR / f"decision_tree_{luong}.pkl")


def ve_confusion_matrix(y_test, du_doan):
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for ax, luong in zip(axes, ["A", "B"]):
        ConfusionMatrixDisplay.from_predictions(y_test, du_doan[luong], cmap="Blues", colorbar=False, ax=ax)
        ax.set_title(f"Decision Tree - Luồng {luong}")
        ax.set_xlabel("Dự đoán")
        ax.set_ylabel("Thực tế")
    fig.tight_layout()
    return fig


def ve_feature_importance(mo_hinh, ten_cot):
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))
    for ax, luong in zip(axes, ["A", "B"]):
        importance = pd.Series(mo_hinh[luong].feature_importances_, index=ten_cot[luong])
        importance.sort_values().tail(10).plot.barh(ax=ax)
        ax.set_title(f"Top 10 đặc trưng quan trọng - Luồng {luong}")
        ax.set_xlabel("Feature importance")
    fig.tight_layout()
    return fig


def ve_cay(model, ten_cot):
    fig, ax = plt.subplots(figsize=(18, 7))
    plot_tree(model, max_depth=2, feature_names=list(ten_cot), class_names=["No", "Yes"],
              filled=True, rounded=True, impurity=False, proportion=True, fontsize=9, ax=ax)
    ax.set_title("Decision Tree - Luồng B (3 tầng đầu)")
    return fig


def main():
    mo_hinh, ten_cot, du_doan = {}, {}, {}

    for luong in ["A", "B"]:
        X_train, X_test, y_train, y_test = doc_du_lieu(luong)
        print(f"\n===== Decision Tree - Luồng {luong} ({X_train.shape[1]} đặc trưng) =====")

        search = tim_tham_so(X_train, y_train)
        print("Tham số tốt nhất:", search.best_params_)
        print(f"F1 cross-validation trên Train: {search.best_score_:.4f}")

        y_pred = search.best_estimator_.predict(X_test)
        metrics = danh_gia_mo_hinh(y_test, y_pred, pos_label=POSITIVE_LABEL)
        luu_ket_qua(luong, search, metrics)

        mo_hinh[luong] = search.best_estimator_
        ten_cot[luong] = X_train.columns
        du_doan[luong] = y_pred

    # Lưu hình để Hùng chèn vào báo cáo
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    hinh = {
        "dt_confusion_matrix.png": ve_confusion_matrix(y_test, du_doan),
        "dt_feature_importance.png": ve_feature_importance(mo_hinh, ten_cot),
        "dt_tree_B.png": ve_cay(mo_hinh["B"], ten_cot["B"]),
    }
    for ten_file, fig in hinh.items():
        fig.savefig(FIGURES_DIR / ten_file, dpi=150, bbox_inches="tight")
        plt.close(fig)

    print("\nĐã lưu: results/duc_decision_tree_A.json, results/duc_decision_tree_B.json,")
    print("        models/decision_tree_A.pkl, models/decision_tree_B.pkl và hình trong report/figures/")


if __name__ == "__main__":
    matplotlib.use("Agg")                     # chỉ lưu hình, không mở cửa sổ
    sys.stdout.reconfigure(encoding="utf-8")  # in được tiếng Việt trên mọi terminal
    main()
