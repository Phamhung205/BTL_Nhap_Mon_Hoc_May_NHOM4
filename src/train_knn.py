"""K-Nearest Neighbors (K-NN) trên Luồng A và Luồng B (phần của Hải).

Chạy từ thư mục gốc dự án:
    python -m src.train_knn

Với mỗi luồng:
1. Đọc dữ liệu X_train, X_test, y_train, y_test do Mạnh và Đức chuẩn bị.
2. Đảm bảo chuẩn hóa dữ liệu:
   - Luồng A: Đã được tiền xử lý và chuẩn hóa ở bước của Mạnh.
   - Luồng B: Cần chuẩn hóa bằng StandardScaler thông qua Pipeline (fit trên từng fold train khi CV).
3. Tinh chỉnh siêu tham số (k, cách đo khoảng cách, weights) bằng GridSearchCV 5-fold trên Train.
4. Đánh giá mô hình tối ưu trên tập Test chung bằng src.evaluate.danh_gia_mo_hinh.
5. Lưu kết quả ra results/hai_knn_A.json, results/hai_knn_B.json và lưu mô hình vào models/.
6. Vẽ ma trận nhầm lẫn (Confusion Matrix) vào report/figures/knn_confusion_matrix.png.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import ConfusionMatrixDisplay, f1_score, make_scorer
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from .config import POSITIVE_LABEL, RANDOM_STATE, TARGET_COLUMN
from .evaluate import danh_gia_mo_hinh

ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT / "data" / "processed"
MODELS_DIR = ROOT / "models"
RESULTS_DIR = ROOT / "results"
FIGURES_DIR = ROOT / "report" / "figures"

PARAM_GRID_A = {
    "n_neighbors": [3, 5, 7, 9, 11, 15, 21, 31, 41, 51],
    "weights": ["uniform", "distance"],
    "metric": ["euclidean", "manhattan"],
}

PARAM_GRID_B = {
    "knn__n_neighbors": [3, 5, 7, 9, 11, 15, 21, 31, 41, 51],
    "knn__weights": ["uniform", "distance"],
    "knn__metric": ["euclidean", "manhattan"],
}


def doc_du_lieu(luong: str):
    """Đọc dữ liệu của Luồng A hoặc B cùng nhãn Train/Test chuẩn."""
    X_train = pd.read_csv(PROCESSED_DIR / f"X_train_{luong}.csv")
    X_test = pd.read_csv(PROCESSED_DIR / f"X_test_{luong}.csv")
    y_train = pd.read_csv(PROCESSED_DIR / "y_train.csv")[TARGET_COLUMN]
    y_test = pd.read_csv(PROCESSED_DIR / "y_test.csv")[TARGET_COLUMN]
    return X_train, X_test, y_train, y_test


def tao_search(luong: str):
    """Tạo GridSearchCV với StratifiedKFold 5-fold, tối ưu F1 cho lớp Churn = Yes."""
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    scorer = make_scorer(f1_score, pos_label=POSITIVE_LABEL)

    if luong == "A":
        estimator = KNeighborsClassifier()
        param_grid = PARAM_GRID_A
    else:
        # Luồng B cần chuẩn hóa StandardScaler để cước phí/tenure không lấn át các đặc trưng khác
        estimator = Pipeline([
            ("scaler", StandardScaler()),
            ("knn", KNeighborsClassifier()),
        ])
        param_grid = PARAM_GRID_B

    return GridSearchCV(
        estimator=estimator,
        param_grid=param_grid,
        scoring=scorer,
        cv=cv,
        n_jobs=-1,
        refit=True,
    )


def luu_ket_qua(luong: str, search: GridSearchCV, metrics: dict):
    """Lưu kết quả JSON theo đúng mẫu result_template.json và lưu model pkl."""
    best_params = search.best_params_.copy()
    if luong == "B":
        # Chuẩn hóa tên tham số bỏ tiền tố "knn__" cho đồng nhất
        best_params = {k.replace("knn__", ""): v for k, v in best_params.items()}

    result = {
        "model_id": f"knn_{luong}",
        "member": "Hải",
        "model": "K-NN",
        "flow": luong,
        "accuracy": metrics["accuracy"],
        "precision": metrics["precision"],
        "recall": metrics["recall"],
        "f1_score": metrics["f1_score"],
        "confusion_matrix": metrics["confusion_matrix"],
        "best_params": best_params,
        "cv_f1": float(search.best_score_),
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_file = RESULTS_DIR / f"hai_knn_{luong}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(search.best_estimator_, MODELS_DIR / f"knn_{luong}.pkl")
    print(f"Đã lưu kết quả: {out_file}")
    print(f"Đã lưu mô hình: {MODELS_DIR / f'knn_{luong}.pkl'}")


def ve_confusion_matrix(y_test, du_doan: dict[str, any]):
    """Vẽ ma trận nhầm lẫn cạnh nhau cho K-NN Luồng A và Luồng B."""
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for ax, luong in zip(axes, ["A", "B"]):
        ConfusionMatrixDisplay.from_predictions(
            y_test,
            du_doan[luong],
            cmap="Greens",
            colorbar=False,
            ax=ax,
        )
        ax.set_title(f"K-NN - Luồng {luong}")
        ax.set_xlabel("Dự đoán")
        ax.set_ylabel("Thực tế")
    fig.tight_layout()
    return fig


def main():
    mo_hinh = {}
    du_doan = {}

    for luong in ["A", "B"]:
        X_train, X_test, y_train, y_test = doc_du_lieu(luong)
        print(f"\n==================================================")
        print(f" Huấn luyện K-NN trên Luồng {luong} ({X_train.shape[1]} đặc trưng)")
        print(f"==================================================")

        search = tao_search(luong)
        search.fit(X_train, y_train)

        print("Tham số tối ưu:", search.best_params_)
        print(f"F1-score CV (Train 5-fold): {search.best_score_:.4f}")

        y_pred = search.best_estimator_.predict(X_test)
        metrics = danh_gia_mo_hinh(y_test, y_pred, pos_label=POSITIVE_LABEL)
        luu_ket_qua(luong, search, metrics)

        mo_hinh[luong] = search.best_estimator_
        du_doan[luong] = y_pred

    # Lưu biểu đồ Confusion Matrix
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig_cm = ve_confusion_matrix(y_test, du_doan)
    fig_path = FIGURES_DIR / "knn_confusion_matrix.png"
    fig_cm.savefig(fig_path, dpi=150, bbox_inches="tight")
    plt.close(fig_cm)
    print(f"\nĐã lưu biểu đồ: {fig_path}")


if __name__ == "__main__":
    matplotlib.use("Agg")
    sys.stdout.reconfigure(encoding="utf-8")
    main()
