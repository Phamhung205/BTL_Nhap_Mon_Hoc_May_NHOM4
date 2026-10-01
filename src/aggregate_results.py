"""Tổng hợp kết quả mô hình cho phần việc của Hùng.

Mỗi thành viên xuất kết quả mô hình thành một file JSON trong thư mục
results/. Sau đó Hùng chạy:

    python -m src.aggregate_results

Chương trình sẽ kiểm tra đủ 4 kết quả và sinh report/model_comparison.csv.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .config import EXPECTED_RESULT_IDS

ROOT = Path(__file__).resolve().parents[1]
RESULT_DIR = ROOT / "results"
OUTPUT_CSV = ROOT / "report" / "model_comparison.csv"

REQUIRED_KEYS = {
    "model_id",
    "member",
    "model",
    "flow",
    "accuracy",
    "precision",
    "recall",
    "f1_score",
    "confusion_matrix",
}


def _load_result(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    missing = REQUIRED_KEYS - set(data)
    if missing:
        raise ValueError(f"{path.name} thiếu trường: {', '.join(sorted(missing))}")

    for key in ("accuracy", "precision", "recall", "f1_score"):
        value = data[key]
        if value is None or not isinstance(value, (int, float)):
            raise ValueError(f"{path.name}: {key} phải là số thực tế, không được để trống.")
        if not 0 <= float(value) <= 1:
            raise ValueError(f"{path.name}: {key} phải nằm trong khoảng [0, 1].")

    return data


def tong_hop_ket_qua(result_dir: Path = RESULT_DIR) -> pd.DataFrame:
    result_dir.mkdir(parents=True, exist_ok=True)
    rows = []

    for path in sorted(result_dir.glob("*.json")):
        if path.name == "result_template.json":
            continue
        rows.append(_load_result(path))

    if not rows:
        raise FileNotFoundError(
            "Chưa có file kết quả JSON trong results/. "
            "Hãy yêu cầu Đức và Hải xuất đủ 4 kết quả theo results/result_template.json."
        )

    found_ids = {row["model_id"] for row in rows}
    unknown_ids = found_ids - set(EXPECTED_RESULT_IDS)
    if unknown_ids:
        raise ValueError("Có model_id không hợp lệ: " + ", ".join(sorted(unknown_ids)))

    duplicate_ids = [mid for mid in found_ids if sum(r["model_id"] == mid for r in rows) > 1]
    if duplicate_ids:
        raise ValueError("Trùng model_id: " + ", ".join(sorted(duplicate_ids)))

    missing_ids = set(EXPECTED_RESULT_IDS) - found_ids
    if missing_ids:
        raise ValueError(
            "Chưa đủ 4 kết quả. Còn thiếu: " + ", ".join(sorted(missing_ids))
        )

    df = pd.DataFrame(rows)
    order_map = {model_id: idx for idx, model_id in enumerate(EXPECTED_RESULT_IDS)}
    df["_order"] = df["model_id"].map(order_map)
    df = df.sort_values("_order").drop(columns="_order")

    columns = [
        "model_id",
        "member",
        "model",
        "flow",
        "accuracy",
        "precision",
        "recall",
        "f1_score",
        "confusion_matrix",
    ]
    return df[columns]


def main():
    df = tong_hop_ket_qua()
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

    print("\n===== BẢNG SO SÁNH 4 KẾT QUẢ =====")
    print(df.to_string(index=False))
    print(f"\nĐã lưu: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
