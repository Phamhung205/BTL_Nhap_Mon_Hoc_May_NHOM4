"""Kiểm tra phần của Đức (Luồng B và Decision Tree).

Chạy từ thư mục gốc dự án:

    python -m unittest discover -s tests -v
"""

import json
import unittest

import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score

from src.feature_engineering_b import tao_dac_trung_B
from src.train_decision_tree import MODELS_DIR, PROCESSED_DIR, RESULTS_DIR, doc_du_lieu


class TestLuongB(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.X_train = pd.read_csv(PROCESSED_DIR / "X_train_raw.csv")
        cls.X_test = pd.read_csv(PROCESSED_DIR / "X_test_raw.csv")

    def test_kich_thuoc_va_khong_thieu_du_lieu(self):
        X_train_B, X_test_B, y_train, y_test = doc_du_lieu("B")
        self.assertEqual(X_train_B.shape, (5634, 17))
        self.assertEqual(X_test_B.shape, (1409, 17))
        self.assertEqual(len(X_train_B), len(y_train))
        self.assertEqual(len(X_test_B), len(y_test))
        self.assertEqual(X_train_B.isna().sum().sum(), 0)
        self.assertEqual(X_test_B.isna().sum().sum(), 0)

    def test_file_csv_khop_voi_ham(self):
        X_train_B, X_test_B, _, _ = doc_du_lieu("B")
        pd.testing.assert_frame_equal(X_train_B, tao_dac_trung_B(self.X_train), check_dtype=False)
        pd.testing.assert_frame_equal(X_test_B, tao_dac_trung_B(self.X_test), check_dtype=False)

    def test_khach_moi_co_tong_cuoc_bang_0(self):
        khach_moi = self.X_train[self.X_train["tenure"] == 0]
        self.assertTrue(khach_moi["TotalCharges"].isna().all())
        self.assertTrue((tao_dac_trung_B(khach_moi)["LogTotalCharges"] == 0).all())

    def test_dac_trung_dem_va_tuong_tac(self):
        B = tao_dac_trung_B(self.X_test)
        for i in range(20):
            row = self.X_test.iloc[i]
            thieu = sum(row[c] == "No" for c in ["OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport"])
            self.assertEqual(B["MissingProtectionCount"].iloc[i], thieu)
            thang_fiber = row["Contract"] == "Month-to-month" and row["InternetService"] == "Fiber optic"
            self.assertEqual(B["MonthToMonth_Fiber"].iloc[i], int(thang_fiber))

    def test_gia_tri_la_bao_loi(self):
        X = self.X_test.head(1).copy()
        X["Contract"] = "Three year"
        with self.assertRaises(ValueError):
            tao_dac_trung_B(X)


class TestDecisionTree(unittest.TestCase):
    def test_ket_qua_json_dung_voi_mo_hinh(self):
        for luong in ["A", "B"]:
            with self.subTest(luong=luong):
                _, X_test, _, y_test = doc_du_lieu(luong)
                model = joblib.load(MODELS_DIR / f"decision_tree_{luong}.pkl")
                y_pred = model.predict(X_test)
                with open(RESULTS_DIR / f"duc_decision_tree_{luong}.json", encoding="utf-8") as f:
                    result = json.load(f)

                self.assertEqual(result["model_id"], f"decision_tree_{luong}")
                self.assertAlmostEqual(result["accuracy"], accuracy_score(y_test, y_pred))
                self.assertAlmostEqual(result["precision"], precision_score(y_test, y_pred, pos_label="Yes"))
                self.assertAlmostEqual(result["recall"], recall_score(y_test, y_pred, pos_label="Yes"))
                self.assertAlmostEqual(result["f1_score"], f1_score(y_test, y_pred, pos_label="Yes"))
                self.assertEqual(result["confusion_matrix"], confusion_matrix(y_test, y_pred).tolist())


if __name__ == "__main__":
    unittest.main()
