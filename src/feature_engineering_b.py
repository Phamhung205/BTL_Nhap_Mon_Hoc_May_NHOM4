"""Luồng B - Feature Engineering (phần của Đức).

Đầu vào : data/processed/X_train_raw.csv, X_test_raw.csv (19 cột gốc, Mạnh đã chia).
Đầu ra  : data/processed/X_train_B.csv, X_test_B.csv (17 đặc trưng).

Chạy từ thư mục gốc dự án:

    python -m src.feature_engineering_b

Mọi phép biến đổi đều làm trên từng dòng, không học gì từ dữ liệu,
nên không có rò rỉ thông tin từ tập Test.

Luồng B không chuẩn hóa vì Decision Tree không cần. Nếu dùng Luồng B cho K-NN
thì cần thêm StandardScaler (fit trên Train).
"""

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT / "data" / "processed"

DICH_VU_BAO_VE = ["OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport"]


def tao_dac_trung_B(X: pd.DataFrame) -> pd.DataFrame:
    """Biến đổi 19 cột gốc thành 17 đặc trưng của Luồng B."""
    hop_dong_thang = X["Contract"] == "Month-to-month"
    fiber = X["InternetService"] == "Fiber optic"
    echeck = X["PaymentMethod"] == "Electronic check"

    # TotalCharges chỉ bị trống ở khách mới (tenure = 0), nên tổng cước = tenure x cước tháng = 0.
    total = X["TotalCharges"].fillna(X["tenure"] * X["MonthlyCharges"])

    B = pd.DataFrame(index=X.index)

    # 1. Giữ nguyên hoặc mã hóa nhị phân (Yes = 1, No = 0)
    B["SeniorCitizen"] = X["SeniorCitizen"]
    B["Partner"] = (X["Partner"] == "Yes").astype(int)
    B["Dependents"] = (X["Dependents"] == "Yes").astype(int)
    B["PaperlessBilling"] = (X["PaperlessBilling"] == "Yes").astype(int)

    # 2. Mã hóa thứ bậc
    B["PhoneLines"] = X["MultipleLines"].map({"No phone service": 0, "No": 1, "Yes": 2})
    B["ContractLength"] = X["Contract"].map({"Month-to-month": 0, "One year": 1, "Two year": 2})

    # 3. Biến số, nhóm thời gian sử dụng (0-12, 13-24, 25-48, >48 tháng), log tổng cước
    B["tenure"] = X["tenure"]
    B["TenureGroup"] = pd.cut(X["tenure"], bins=[-1, 12, 24, 48, np.inf], labels=False)
    B["MonthlyCharges"] = X["MonthlyCharges"]
    B["LogTotalCharges"] = np.log1p(total)

    # 4. Internet và phương thức thanh toán
    B["HasInternet"] = (X["InternetService"] != "No").astype(int)
    B["IsFiber"] = fiber.astype(int)
    B["IsElectronicCheck"] = echeck.astype(int)
    B["IsAutoPayment"] = X["PaymentMethod"].str.contains("automatic").astype(int)

    # 5. Số dịch vụ bảo vệ / hỗ trợ còn thiếu (0-4)
    B["MissingProtectionCount"] = (X[DICH_VU_BAO_VE] == "No").sum(axis=1)

    # 6. Đặc trưng tương tác
    B["MonthToMonth_Fiber"] = (hop_dong_thang & fiber).astype(int)
    B["MonthToMonth_ElectronicCheck"] = (hop_dong_thang & echeck).astype(int)

    # Không dùng: gender, StreamingTV, StreamingMovies (ít liên quan tới Churn).

    if B.isna().any().any():
        raise ValueError("Dữ liệu có giá trị lạ (ví dụ Contract hoặc MultipleLines không hợp lệ).")
    return B


def main():
    for split in ["train", "test"]:
        X = pd.read_csv(PROCESSED_DIR / f"X_{split}_raw.csv")
        X_B = tao_dac_trung_B(X)
        X_B.to_csv(PROCESSED_DIR / f"X_{split}_B.csv", index=False)
        print(f"Đã lưu X_{split}_B.csv: {X_B.shape}")


if __name__ == "__main__":
    main()
