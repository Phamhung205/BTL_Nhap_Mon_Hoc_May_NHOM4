"""Feature Engineering cho Luong B cua Duc.

Module nay chi doc cac tap raw da duoc Manh chia san. Bo bien doi duoc ``fit``
tren Train de hoc trung vi, gia tri pho bien va cac muc phan loai; Test chi duoc
``transform``. Thu tu dong dau vao luon duoc giu nguyen.
"""

from __future__ import annotations

import csv
import math
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from statistics import median
from typing import Iterable

import joblib


ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT / "data" / "processed"
MODELS_DIR = ROOT / "models"

RAW_NUMERIC_COLUMNS = (
    "SeniorCitizen",
    "tenure",
    "MonthlyCharges",
    "TotalCharges",
)

RAW_CATEGORICAL_COLUMNS = (
    "gender",
    "Partner",
    "Dependents",
    "PhoneService",
    "MultipleLines",
    "InternetService",
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
    "Contract",
    "PaperlessBilling",
    "PaymentMethod",
)

INTERNET_SERVICE_COLUMNS = (
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
)

PROTECTION_COLUMNS = (
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
)

ENGINEERED_NUMERIC_COLUMNS = (
    "AverageMonthlySpend",
    "MonthlyVsAverageGap",
    "ActiveInternetServices",
    "ProtectionServices",
    "StreamingServices",
    "FamilyConnections",
    "IsNewCustomer",
    "IsMonthToMonth",
    "UsesFiberOptic",
    "UsesElectronicCheck",
    "UsesAutomaticPayment",
    "NoOnlineSecurity",
    "NoTechSupport",
    "MonthToMonthFiber",
    "MonthToMonthElectronicCheck",
    "RiskServiceGap",
)

ENGINEERED_CATEGORICAL_COLUMNS = ("TenureBand",)

# Lua chon dua tren cac bien noi bat trong EDA, sau do so sanh bang CV chi tren
# Train. Ba bien tuong tac ben duoi giup Luong B khac Luong A ma khong dung nhan
# cua Test de ra quyet dinh.
SELECTED_NUMERIC_COLUMNS = RAW_NUMERIC_COLUMNS + (
    "MonthToMonthFiber",
    "MonthToMonthElectronicCheck",
    "RiskServiceGap",
)

SELECTED_CATEGORICAL_COLUMNS = (
    "Partner",
    "Dependents",
    "InternetService",
    "OnlineSecurity",
    "TechSupport",
    "Contract",
    "PaperlessBilling",
    "PaymentMethod",
)

REQUIRED_COLUMNS = set(RAW_NUMERIC_COLUMNS + RAW_CATEGORICAL_COLUMNS)


def read_raw_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    """Doc CSV thanh cac dong co thu tu, khong sap xep hay chia lai du lieu."""
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"{path} khong co dong tieu de.")
        rows = list(reader)
        return rows, list(reader.fieldnames)


def _parse_float(value: str | None) -> float | None:
    if value is None or not value.strip():
        return None
    parsed = float(value)
    return parsed if math.isfinite(parsed) else None


def _most_frequent(values: Iterable[str]) -> str:
    counts = Counter(value for value in values if value)
    if not counts:
        raise ValueError("Khong the tim gia tri pho bien cho cot rong.")
    # Sap xep tie-break de ket qua tai lap tren moi may.
    return min(counts, key=lambda value: (-counts[value], value))


def _tenure_band(tenure: float) -> str:
    if tenure <= 6:
        return "0-6"
    if tenure <= 12:
        return "7-12"
    if tenure <= 24:
        return "13-24"
    if tenure <= 48:
        return "25-48"
    if tenure <= 60:
        return "49-60"
    return "61+"


@dataclass
class FeatureEngineerB:
    """Bo bien doi Luong B co giao dien ``fit``/``transform`` ro rang."""

    numeric_medians_: dict[str, float] = field(default_factory=dict)
    categorical_modes_: dict[str, str] = field(default_factory=dict)
    categorical_levels_: dict[str, list[str]] = field(default_factory=dict)
    feature_names_: list[str] = field(default_factory=list)
    fitted_: bool = False

    def _validate_columns(self, rows: list[dict[str, str]]) -> None:
        if not rows:
            raise ValueError("Du lieu dau vao rong.")
        missing = REQUIRED_COLUMNS - set(rows[0])
        if missing:
            raise ValueError("Thieu cot bat buoc: " + ", ".join(sorted(missing)))

    def fit(self, train_rows: list[dict[str, str]]) -> "FeatureEngineerB":
        """Chi hoc quy tac dien thieu va muc one-hot tu Train."""
        self._validate_columns(train_rows)

        self.numeric_medians_ = {}
        for column in RAW_NUMERIC_COLUMNS:
            values = [
                parsed
                for row in train_rows
                if (parsed := _parse_float(row.get(column))) is not None
            ]
            if not values:
                raise ValueError(f"Cot so {column} khong co gia tri hop le.")
            self.numeric_medians_[column] = float(median(values))

        self.categorical_modes_ = {
            column: _most_frequent(row.get(column, "") for row in train_rows)
            for column in RAW_CATEGORICAL_COLUMNS
        }

        enriched_rows = [self._enrich_row(row) for row in train_rows]
        self.categorical_levels_ = {
            column: sorted({str(row[column]) for row in enriched_rows})
            for column in SELECTED_CATEGORICAL_COLUMNS
        }

        feature_names = list(SELECTED_NUMERIC_COLUMNS)
        for column in SELECTED_CATEGORICAL_COLUMNS:
            feature_names.extend(
                f"{column}__{level}"
                for level in self.categorical_levels_[column]
            )

        self.feature_names_ = feature_names
        self.fitted_ = True
        return self

    def _enrich_row(self, row: dict[str, str]) -> dict[str, float | str]:
        numeric = {
            column: (
                self.numeric_medians_[column]
                if _parse_float(row.get(column)) is None
                else float(_parse_float(row.get(column)))
            )
            for column in RAW_NUMERIC_COLUMNS
        }
        categorical = {
            column: row.get(column, "") or self.categorical_modes_[column]
            for column in RAW_CATEGORICAL_COLUMNS
        }

        tenure = numeric["tenure"]
        monthly_charges = numeric["MonthlyCharges"]
        total_charges = numeric["TotalCharges"]

        # tenure=0 la khach hang moi va TotalCharges thuong bi thieu; dung muc phi
        # hien tai thay vi chia cho 0. Quy tac nay khong tham chieu nhan Churn.
        average_monthly_spend = (
            total_charges / tenure if tenure > 0 else monthly_charges
        )

        active_services = sum(
            categorical[column] == "Yes" for column in INTERNET_SERVICE_COLUMNS
        )
        protection_services = sum(
            categorical[column] == "Yes" for column in PROTECTION_COLUMNS
        )
        streaming_services = sum(
            categorical[column] == "Yes"
            for column in ("StreamingTV", "StreamingMovies")
        )
        family_connections = sum(
            categorical[column] == "Yes" for column in ("Partner", "Dependents")
        )

        is_month_to_month = int(categorical["Contract"] == "Month-to-month")
        uses_fiber = int(categorical["InternetService"] == "Fiber optic")
        uses_electronic_check = int(
            categorical["PaymentMethod"] == "Electronic check"
        )
        uses_automatic_payment = int(
            categorical["PaymentMethod"]
            in {"Bank transfer (automatic)", "Credit card (automatic)"}
        )
        no_security = int(categorical["OnlineSecurity"] == "No")
        no_support = int(categorical["TechSupport"] == "No")

        return {
            **numeric,
            **categorical,
            "AverageMonthlySpend": average_monthly_spend,
            "MonthlyVsAverageGap": monthly_charges - average_monthly_spend,
            "ActiveInternetServices": active_services,
            "ProtectionServices": protection_services,
            "StreamingServices": streaming_services,
            "FamilyConnections": family_connections,
            "IsNewCustomer": int(tenure <= 6),
            "IsMonthToMonth": is_month_to_month,
            "UsesFiberOptic": uses_fiber,
            "UsesElectronicCheck": uses_electronic_check,
            "UsesAutomaticPayment": uses_automatic_payment,
            "NoOnlineSecurity": no_security,
            "NoTechSupport": no_support,
            "MonthToMonthFiber": is_month_to_month * uses_fiber,
            "MonthToMonthElectronicCheck": (
                is_month_to_month * uses_electronic_check
            ),
            "RiskServiceGap": no_security + no_support,
            "TenureBand": _tenure_band(tenure),
        }

    def transform(self, rows: list[dict[str, str]]) -> list[list[float]]:
        """Ap dung dung quy tac da hoc, khong ``fit`` lai tren Test."""
        if not self.fitted_:
            raise RuntimeError("Can goi fit(train_rows) truoc transform.")
        self._validate_columns(rows)

        matrix: list[list[float]] = []

        for raw_row in rows:
            row = self._enrich_row(raw_row)
            values = [
                float(row[column])
                for column in SELECTED_NUMERIC_COLUMNS
            ]

            for column in SELECTED_CATEGORICAL_COLUMNS:
                value = str(row[column])
                values.extend(
                    1.0 if value == level else 0.0
                    for level in self.categorical_levels_[column]
                )

            if not all(math.isfinite(value) for value in values):
                raise ValueError("Luong B sinh ra gia tri khong huu han.")
            matrix.append(values)

        return matrix

    def fit_transform(self, train_rows: list[dict[str, str]]) -> list[list[float]]:
        return self.fit(train_rows).transform(train_rows)


def write_matrix_csv(
    path: Path,
    feature_names: list[str],
    matrix: list[list[float]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(feature_names)
        writer.writerows(matrix)


def build_flow_b(
    train_path: Path = PROCESSED_DIR / "X_train_raw.csv",
    test_path: Path = PROCESSED_DIR / "X_test_raw.csv",
) -> tuple[FeatureEngineerB, list[list[float]], list[list[float]]]:
    train_rows, train_columns = read_raw_csv(train_path)
    test_rows, test_columns = read_raw_csv(test_path)

    if train_columns != test_columns:
        raise ValueError("Train/Test raw khong co cung thu tu cot.")

    transformer = FeatureEngineerB()
    train_matrix = transformer.fit_transform(train_rows)
    test_matrix = transformer.transform(test_rows)

    if len(train_matrix) != len(train_rows) or len(test_matrix) != len(test_rows):
        raise AssertionError("Luong B lam thay doi so dong.")
    if train_matrix and test_matrix:
        if len(train_matrix[0]) != len(test_matrix[0]):
            raise AssertionError("So cot Train/Test Luong B khong khop.")

    return transformer, train_matrix, test_matrix


def main() -> None:
    transformer, train_matrix, test_matrix = build_flow_b()

    train_output = PROCESSED_DIR / "X_train_B.csv"
    test_output = PROCESSED_DIR / "X_test_B.csv"
    write_matrix_csv(train_output, transformer.feature_names_, train_matrix)
    write_matrix_csv(test_output, transformer.feature_names_, test_matrix)

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    transformer_path = MODELS_DIR / "feature_engineer_B.pkl"
    joblib.dump(transformer, transformer_path)

    print(f"X_train_B: ({len(train_matrix)}, {len(transformer.feature_names_)})")
    print(f"X_test_B : ({len(test_matrix)}, {len(transformer.feature_names_)})")
    print(f"Da luu: {train_output}")
    print(f"Da luu: {test_output}")
    print(f"Da luu: {transformer_path}")


if __name__ == "__main__":
    main()
