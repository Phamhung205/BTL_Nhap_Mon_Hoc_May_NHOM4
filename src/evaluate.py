"""Các hàm đánh giá mô hình dùng thống nhất cho Decision Tree và K-NN."""

from __future__ import annotations

from typing import Any

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

from .config import POSITIVE_LABEL


def _resolve_positive_label(y_true, pos_label=None):
    """Chọn nhãn dương cho bài toán Churn.

    Ưu tiên nhãn do người gọi truyền vào. Nếu dữ liệu còn ở dạng Yes/No
    thì dùng 'Yes'; nếu đã mã hóa 0/1 thì dùng 1.
    """
    if pos_label is not None:
        return pos_label

    labels = set(y_true)
    if POSITIVE_LABEL in labels:
        return POSITIVE_LABEL
    if 1 in labels:
        return 1

    raise ValueError(
        "Không xác định được nhãn dương. Hãy truyền pos_label='Yes' hoặc pos_label=1."
    )


def danh_gia_mo_hinh(y_true, y_pred, pos_label=None, in_chi_tiet=True) -> dict[str, Any]:
    """Tính các metric cần cho báo cáo của Hùng.

    Precision/Recall/F1 được tính cho lớp dương (khách hàng Churn),
    phù hợp hơn việc chỉ nhìn Accuracy khi dữ liệu có thể mất cân bằng.
    """
    positive = _resolve_positive_label(y_true, pos_label)

    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, pos_label=positive, zero_division=0)
    recall = recall_score(y_true, y_pred, pos_label=positive, zero_division=0)
    f1 = f1_score(y_true, y_pred, pos_label=positive, zero_division=0)
    cm = confusion_matrix(y_true, y_pred).tolist()

    result = {
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1_score": float(f1),
        "confusion_matrix": cm,
        "positive_label": positive,
    }

    if in_chi_tiet:
        print("===== KẾT QUẢ ĐÁNH GIÁ =====")
        print(f"Accuracy : {accuracy:.4f}")
        print(f"Precision: {precision:.4f}")
        print(f"Recall   : {recall:.4f}")
        print(f"F1-score : {f1:.4f}")
        print("\n===== CONFUSION MATRIX =====")
        print(cm)
        print("\n===== CLASSIFICATION REPORT =====")
        print(classification_report(y_true, y_pred, zero_division=0))

    return result
