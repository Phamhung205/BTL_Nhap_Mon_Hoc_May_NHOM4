"""Phân tích lỗi (Error Analysis) trên tập Test chung (phần của Hải).

Chạy từ thư mục gốc dự án:
    python -m src.error_analysis

Nhiệm vụ:
1. Đọc mô hình tốt nhất đã chốt (Decision Tree Luồng A có F1 cao nhất 0.6258, và K-NN Luồng A có F1 cao nhất 0.5992).
2. Dự đoán trên tập Test chung, phân loại từng khách hàng thành:
   - TP: Đoán đúng khách rời bỏ (True Positive)
   - TN: Đoán đúng khách ở lại (True Negative)
   - FP: Đoán nhầm khách ở lại thành rời bỏ (False Positive)
   - FN: Bỏ sót khách rời bỏ, đoán là ở lại (False Negative - rủi ro kinh doanh cao nhất)
3. Phân tích nguyên nhân lỗi dựa trên thông tin gốc (X_test_raw.csv):
   - Loại hợp đồng (Contract)
   - Thời gian gắn bó (tenure)
   - Cước hàng tháng (MonthlyCharges)
   - Dịch vụ Internet và dịch vụ bảo vệ
4. Xuất các mẫu sai tiêu biểu ra results/error_cases_sample.csv.
5. Vẽ biểu đồ phân tích lỗi vào report/figures/error_analysis_*.png để Hùng đưa vào báo cáo LaTeX.
"""

from __future__ import annotations

import sys
from pathlib import Path

import joblib
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from .config import POSITIVE_LABEL, TARGET_COLUMN

ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT / "data" / "processed"
MODELS_DIR = ROOT / "models"
RESULTS_DIR = ROOT / "results"
FIGURES_DIR = ROOT / "report" / "figures"


def phan_loai_du_doan(y_true: pd.Series, y_pred: np.ndarray) -> pd.Series:
    """Gán nhãn TP, TN, FP, FN cho từng dòng."""
    nhan = []
    for true_val, pred_val in zip(y_true, y_pred):
        if true_val == "Yes" and pred_val == "Yes":
            nhan.append("TP (Đoán đúng Churn)")
        elif true_val == "No" and pred_val == "No":
            nhan.append("TN (Đoán đúng Ở lại)")
        elif true_val == "No" and pred_val == "Yes":
            nhan.append("FP (Nhầm thành Churn)")
        else:
            nhan.append("FN (Bỏ sót Churn)")
    return pd.Series(nhan, index=y_true.index, name="Prediction_Type")


def phan_tich_loi(model_name: str, luong: str = "A"):
    """Thực hiện phân tích lỗi chi tiết cho một mô hình trên tập Test."""
    X_test_model = pd.read_csv(PROCESSED_DIR / f"X_test_{luong}.csv")
    y_test = pd.read_csv(PROCESSED_DIR / "y_test.csv")[TARGET_COLUMN]
    X_test_raw = pd.read_csv(PROCESSED_DIR / "X_test_raw.csv")

    model_file = MODELS_DIR / f"{model_name}_{luong}.pkl"
    if not model_file.exists():
        raise FileNotFoundError(f"Không tìm thấy mô hình: {model_file}")

    model = joblib.load(model_file)
    y_pred = model.predict(X_test_model)

    df_loi = X_test_raw.copy()
    df_loi["Actual"] = y_test
    df_loi["Predicted"] = y_pred
    df_loi["Prediction_Type"] = phan_loai_du_doan(y_test, y_pred)

    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(X_test_model)
        # Xác suất Churn = Yes
        pos_idx = list(model.classes_).index(POSITIVE_LABEL)
        df_loi["Churn_Probability"] = probs[:, pos_idx]

    return df_loi


def ve_bieu_do_loi(df_loi: pd.DataFrame, model_title: str):
    """Vẽ biểu đồ phân tích lỗi theo thời gian gắn bó, cước phí và loại hợp đồng."""
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    order = ["TP (Đoán đúng Churn)", "TN (Đoán đúng Ở lại)", "FP (Nhầm thành Churn)", "FN (Bỏ sót Churn)"]
    palette = ["#2ecc71", "#3498db", "#e67e22", "#e74c3c"]

    # 1. Phân bố tenure theo nhóm dự đoán
    sns.boxplot(
        data=df_loi,
        x="Prediction_Type",
        y="tenure",
        hue="Prediction_Type",
        order=order,
        palette=palette,
        legend=False,
        ax=axes[0],
    )
    axes[0].set_title(f"Thời gian gắn bó (Tenure)\ntheo nhóm dự đoán ({model_title})")
    axes[0].set_xlabel("")
    axes[0].set_ylabel("Tháng gắn bó (tenure)")
    axes[0].tick_params(axis="x", rotation=15)

    # 2. Phân bố MonthlyCharges theo nhóm dự đoán
    sns.boxplot(
        data=df_loi,
        x="Prediction_Type",
        y="MonthlyCharges",
        hue="Prediction_Type",
        order=order,
        palette=palette,
        legend=False,
        ax=axes[1],
    )
    axes[1].set_title(f"Cước phí hàng tháng (Monthly Charges)\ntheo nhóm dự đoán ({model_title})")
    axes[1].set_xlabel("")
    axes[1].set_ylabel("Cước phí ($/tháng)")
    axes[1].tick_params(axis="x", rotation=15)

    # 3. Phân bố tỷ lệ lỗi theo loại hợp đồng (Contract)
    ct = pd.crosstab(df_loi["Contract"], df_loi["Prediction_Type"], normalize="index") * 100
    cols_order = [c for c in ["TP (Đoán đúng Churn)", "TN (Đoán đúng Ở lại)", "FP (Nhầm thành Churn)", "FN (Bỏ sót Churn)"] if c in ct.columns]
    ct[cols_order].plot(
        kind="bar",
        stacked=True,
        color=["#2ecc71", "#3498db", "#e67e22", "#e74c3c"],
        ax=axes[2],
    )
    axes[2].set_title(f"Tỷ lệ kết quả dự đoán theo loại hợp đồng\n({model_title})")
    axes[2].set_xlabel("Loại hợp đồng")
    axes[2].set_ylabel("Tỷ lệ (%)")
    axes[2].legend(title="Nhóm dự đoán", bbox_to_anchor=(1.02, 1), loc="upper left")
    axes[2].tick_params(axis="x", rotation=0)

    fig.tight_layout()
    return fig


def main():
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print("==================================================")
    print(" BẮT ĐẦU PHÂN TÍCH LỖI (ERROR ANALYSIS) - HẢI")
    print("==================================================")

    # Phân tích mô hình tốt nhất (Decision Tree Luồng A) và mô hình K-NN tốt nhất (K-NN Luồng A)
    for model_name, title in [("decision_tree", "Decision Tree Luồng A"), ("knn", "K-NN Luồng A")]:
        df_loi = phan_tich_loi(model_name=model_name, luong="A")

        so_luong = df_loi["Prediction_Type"].value_counts()
        print(f"\n--- Thống kê nhóm dự đoán ({title}) ---")
        for k, v in so_luong.items():
            print(f"  {k:25s}: {v:4d} khách hàng ({v/len(df_loi)*100:.1f}%)")

        # Lưu biểu đồ phân tích lỗi
        fig = ve_bieu_do_loi(df_loi, title)
        fig_path = FIGURES_DIR / f"error_analysis_{model_name}.png"
        fig.savefig(fig_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"  -> Đã lưu biểu đồ: {fig_path}")

        # Trích xuất phân tích chi tiết nhóm FN và FP
        fn_cases = df_loi[df_loi["Prediction_Type"] == "FN (Bỏ sót Churn)"]
        fp_cases = df_loi[df_loi["Prediction_Type"] == "FP (Nhầm thành Churn)"]

        print(f"\n  [Nguyên nhân False Negatives - Bỏ sót Churn]")
        print(f"    - Thời gian gắn bó trung bình: {fn_cases['tenure'].mean():.1f} tháng (so với TP là {df_loi[df_loi['Prediction_Type']=='TP (Đoán đúng Churn)']['tenure'].mean():.1f} tháng)")
        print(f"    - Cước tháng trung bình: ${fn_cases['MonthlyCharges'].mean():.1f} (so với TP là ${df_loi[df_loi['Prediction_Type']=='TP (Đoán đúng Churn)']['MonthlyCharges'].mean():.1f})")
        print(f"    - Cơ cấu hợp đồng FN: {dict(fn_cases['Contract'].value_counts())}")

        print(f"\n  [Nguyên nhân False Positives - Nhầm là Churn]")
        print(f"    - Thời gian gắn bó trung bình: {fp_cases['tenure'].mean():.1f} tháng")
        print(f"    - Cước tháng trung bình: ${fp_cases['MonthlyCharges'].mean():.1f}")
        print(f"    - Cơ cấu hợp đồng FP: {dict(fp_cases['Contract'].value_counts())}")

        if model_name == "decision_tree":
            # Xuất mẫu 30 khách hàng lỗi tiêu biểu để nhóm dễ tra cứu
            cols_to_export = [
                "Contract", "tenure", "MonthlyCharges", "PaymentMethod", "InternetService",
                "Actual", "Predicted", "Prediction_Type"
            ]
            if "Churn_Probability" in df_loi.columns:
                cols_to_export.append("Churn_Probability")
            mau_loi = pd.concat([fn_cases.head(15), fp_cases.head(15)])[cols_to_export].reset_index(names="Customer_Index")
            csv_path = RESULTS_DIR / "error_cases_sample.csv"
            mau_loi.to_csv(csv_path, index=False)
            print(f"  -> Đã xuất 30 ca lỗi tiêu biểu ra: {csv_path}")

    print("\nHoàn thành phân tích lỗi thành công!")


if __name__ == "__main__":
    matplotlib.use("Agg")
    sys.stdout.reconfigure(encoding="utf-8")
    main()
