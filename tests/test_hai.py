"""Kiểm tra phần của Hải (K-NN và kết quả đánh giá).

Chạy từ thư mục gốc dự án:
    python -m unittest discover -s tests -v
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

from src.train_knn import MODELS_DIR, PROCESSED_DIR, RESULTS_DIR, doc_du_lieu


class TestKNN(unittest.TestCase):
    def test_ket_qua_json_dung_voi_mo_hinh(self):
        for luong in ["A", "B"]:
            with self.subTest(luong=luong):
                _, X_test, _, y_test = doc_du_lieu(luong)
                model_path = MODELS_DIR / f"knn_{luong}.pkl"
                self.assertTrue(model_path.exists(), f"Không tìm thấy file {model_path}")
                model = joblib.load(model_path)
                y_pred = model.predict(X_test)

                json_path = RESULTS_DIR / f"hai_knn_{luong}.json"
                self.assertTrue(json_path.exists(), f"Không tìm thấy file {json_path}")
                with open(json_path, encoding="utf-8") as f:
                    result = json.load(f)

                self.assertEqual(result["model_id"], f"knn_{luong}")
                self.assertEqual(result["member"], "Hải")
                self.assertEqual(result["model"], "K-NN")
                self.assertEqual(result["flow"], luong)
                self.assertAlmostEqual(result["accuracy"], accuracy_score(y_test, y_pred))
                self.assertAlmostEqual(result["precision"], precision_score(y_test, y_pred, pos_label="Yes"))
                self.assertAlmostEqual(result["recall"], recall_score(y_test, y_pred, pos_label="Yes"))
                self.assertAlmostEqual(result["f1_score"], f1_score(y_test, y_pred, pos_label="Yes"))
                self.assertEqual(result["confusion_matrix"], confusion_matrix(y_test, y_pred).tolist())


if __name__ == "__main__":
    unittest.main()
