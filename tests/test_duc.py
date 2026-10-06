"""Regression, independent-reference and end-to-end checks for Duc's work."""
import copy
import csv
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch

import joblib
import numpy as np
from sklearn.base import clone
from sklearn.exceptions import NotFittedError

from src.duc_preprocessing import FeatureEngineerB, TelcoPreprocessor, NUMERIC, CATEGORICAL
from src.feature_engineering_b import read_raw_csv, build_flow_b
from src.train_decision_tree import load_numeric_matrix, load_target, tune_decision_tree, make_cv

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/processed"


class PreprocessingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.train, _ = read_raw_csv(DATA / "X_train_raw.csv")
        cls.test, _ = read_raw_csv(DATA / "X_test_raw.csv")

    def test_a_matches_supplied_csv_and_original_sklearn_transformer(self):
        # Independent original artifact, not merely this implementation again.
        import pandas as pd
        original = joblib.load(ROOT / "models/preprocessor_A.pkl")
        fresh = TelcoPreprocessor("A").fit(self.train)
        for split, rows in (("train", self.train), ("test", self.test)):
            saved, columns = load_numeric_matrix(DATA / f"X_{split}_A.csv")
            native = original.transform(pd.read_csv(DATA / f"X_{split}_raw.csv"))
            np.testing.assert_allclose(native, saved, rtol=1e-10, atol=1e-10)
            np.testing.assert_allclose(fresh.transform(rows), native, rtol=1e-10, atol=1e-10)
            self.assertEqual(columns, fresh.feature_names_)

    def test_b_row_order_and_interactions_independently(self):
        transformer, train, test = build_flow_b()
        for rows, matrix, expected in ((self.train, train, 5634), (self.test, test, 1409)):
            self.assertEqual(matrix.shape, (expected, 29))
            for row, values in zip(rows, matrix):
                self.assertEqual(values[1], float(row['tenure']))
                self.assertEqual(values[2], float(row['MonthlyCharges']))
                self.assertEqual(values[4], int(row['Contract']=='Month-to-month' and row['InternetService']=='Fiber optic'))
                self.assertEqual(values[5], int(row['Contract']=='Month-to-month' and row['PaymentMethod']=='Electronic check'))
                self.assertEqual(values[6], int(row['OnlineSecurity']=='No')+int(row['TechSupport']=='No'))
        self.assertEqual(len(set(transformer.feature_names_)), 29)

    def test_transform_has_no_test_learning_and_handles_unknown(self):
        model = FeatureEngineerB().fit(self.train)
        state = joblib.hash(model)
        rows = copy.deepcopy(self.test[:2])
        rows[0]['Contract'] = 'New unseen contract'
        rows[0]['TotalCharges'] = ' '
        rows[0]['tenure'] = '0'
        rows[1]['MonthlyCharges'] = '999999'
        transformed = model.transform(rows)
        self.assertEqual(state, joblib.hash(model))
        self.assertEqual(transformed[0, 3], model.numeric_medians_['TotalCharges'])
        self.assertTrue(np.isfinite(transformed).all())
        block = [i for i, name in enumerate(model.feature_names_) if name.startswith('Contract__')]
        self.assertTrue((transformed[0, block] == 0).all())

    def test_reordering_rows_only_reorders_output(self):
        model = FeatureEngineerB().fit(self.train)
        subset = self.test[:25]
        order = np.random.default_rng(42).permutation(len(subset))
        np.testing.assert_array_equal(model.transform([subset[i] for i in order]), model.transform(subset)[order])

    def test_invalid_input_and_clone(self):
        with self.assertRaises(NotFittedError):
            FeatureEngineerB().transform(self.test[:1])
        model = FeatureEngineerB().fit(self.train)
        self.assertFalse(hasattr(clone(model), 'feature_names_'))
        for change in ('missing', 'infinity', 'nonnumeric'):
            rows = copy.deepcopy(self.test[:2])
            if change == 'missing':
                del rows[1]['Contract']
            else:
                rows[0]['MonthlyCharges'] = 'inf' if change == 'infinity' else 'abc'
            with self.assertRaises(ValueError):
                model.transform(rows)
        with self.assertRaises(ValueError):
            model.transform([])

    def test_gridsearch_really_fits_each_fold_separately(self):
        rows = copy.deepcopy(self.train[:30])
        labels = np.array(['No', 'Yes'] * 15, dtype=object)
        for i, row in enumerate(rows):
            row['TotalCharges'] = str(i * 100)
        rows[0]['TotalCharges'] = ''
        observed = []
        original_fit = TelcoPreprocessor.fit

        def tracked_fit(instance, X, y=None):
            fitted = original_fit(instance, X, y)
            observed.append((len(X), fitted.numeric_medians_['TotalCharges']))
            return fitted

        expected = []
        for train_idx, val_idx in make_cv().split(rows, labels):
            values = [float(rows[i]['TotalCharges']) for i in train_idx if rows[i]['TotalCharges']]
            expected.append((len(train_idx), float(np.median(values))))
        expected.append((len(rows), float(np.median([float(r['TotalCharges']) for r in rows if r['TotalCharges']]))))
        with patch.object(TelcoPreprocessor, 'fit', tracked_fit):
            search = tune_decision_tree(rows, labels, 'B', n_jobs=1,
                                       param_grid={'tree__max_depth': [2]})
        self.assertEqual(observed, expected)
        self.assertIsNone(search.best_estimator_.memory)

    def test_csv_readers_reject_duplicate_headers_and_ragged_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'bad.csv'
            for contents in ('a,a\n1,2\n', 'a,b\n1\n', 'a,b\n1,2,3\n'):
                path.write_text(contents, encoding='utf-8')
                for loader in (read_raw_csv, load_numeric_matrix):
                    with self.assertRaises(ValueError):
                        loader(path)

    def test_serial_and_parallel_search_agree(self):
        rows = self.train[:100]
        labels = load_target(DATA / 'y_train.csv')[:100]
        grid = {'tree__max_depth': [2, 3]}
        serial = tune_decision_tree(rows, labels, 'B', n_jobs=1, param_grid=grid)
        parallel = tune_decision_tree(rows, labels, 'B', n_jobs=2, param_grid=grid)
        self.assertEqual(serial.best_params_, parallel.best_params_)
        np.testing.assert_array_equal(serial.cv_results_['mean_test_score'], parallel.cv_results_['mean_test_score'])
        np.testing.assert_array_equal(serial.predict(self.test[:20]), parallel.predict(self.test[:20]))

    def test_cli_artifact_loads_in_fresh_process(self):
        with tempfile.TemporaryDirectory(prefix='duc-cli-test-') as tmp:
            work = Path(tmp)
            shutil.copytree(ROOT / 'src', work / 'src', ignore=shutil.ignore_patterns('__pycache__'))
            shutil.copytree(DATA, work / 'data/processed')
            run = subprocess.run([sys.executable, '-m', 'src.feature_engineering_b'],
                                 cwd=work, capture_output=True, text=True, timeout=90)
            self.assertEqual(run.returncode, 0, run.stderr)
            code = (
                "import joblib,numpy as np; "
                "from src.feature_engineering_b import read_raw_csv; "
                "from src.train_decision_tree import load_numeric_matrix; "
                "t=joblib.load('models/feature_engineer_B.pkl'); "
                "rows,_=read_raw_csv('data/processed/X_test_raw.csv'); "
                "saved,_=load_numeric_matrix('data/processed/X_test_B.csv'); "
                "assert type(t).__module__=='src.duc_preprocessing'; "
                "np.testing.assert_array_equal(t.transform(rows),saved)"
            )
            reload = subprocess.run([sys.executable, '-c', code], cwd=work,
                                    capture_output=True, text=True, timeout=90)
            self.assertEqual(reload.returncode, 0, reload.stderr)


class DeliveredArtifactTests(unittest.TestCase):
    def test_input_hashes_and_source_labels(self):
        manifest = json.loads((ROOT / 'report/duc_run_manifest.json').read_text(encoding='utf-8'))
        for name, expected in manifest['sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), expected, name)
        raw, columns = read_raw_csv(ROOT / 'data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv')
        features = [c for c in columns if c not in ('customerID', 'Churn')]
        def key(row):
            return tuple((float(row[c]) if row[c].strip() else None) if c in NUMERIC else row[c] for c in features)
        source = Counter((key(row), row['Churn']) for row in raw)
        delivered = Counter()
        for split in ('train', 'test'):
            rows, _ = read_raw_csv(DATA / f'X_{split}_raw.csv')
            labels = load_target(DATA / f'y_{split}.csv')
            self.assertEqual(len(rows), len(labels))
            delivered.update((key(row), label) for row, label in zip(rows, labels))
        self.assertEqual(source, delivered)

    def test_models_predictions_and_manual_metrics(self):
        from src.aggregate_results import _load_result
        rows, _ = read_raw_csv(DATA / 'X_test_raw.csv')
        y = load_target(DATA / 'y_test.csv')
        for flow in ('A', 'B'):
            result = _load_result(ROOT / f'results/duc_decision_tree_{flow}.json')
            X, _ = load_numeric_matrix(DATA / f'X_test_{flow}.csv')
            tree = joblib.load(ROOT / f'models/decision_tree_{flow}.pkl')
            pipeline = joblib.load(ROOT / f'models/decision_tree_{flow}_pipeline.pkl')
            pred = tree.predict(X)
            np.testing.assert_array_equal(pred, pipeline.predict(rows))
            train_raw, _ = read_raw_csv(DATA / 'X_train_raw.csv')
            train_csv, _ = load_numeric_matrix(DATA / f'X_train_{flow}.csv')
            np.testing.assert_array_equal(tree.predict(train_csv), pipeline.predict(train_raw))
            tn = int(sum((y=='No') & (pred=='No')))
            fp = int(sum((y=='No') & (pred=='Yes')))
            fn = int(sum((y=='Yes') & (pred=='No')))
            tp = int(sum((y=='Yes') & (pred=='Yes')))
            self.assertEqual(result['confusion_matrix'], [[tn,fp],[fn,tp]])
            self.assertAlmostEqual(result['accuracy'], (tn+tp)/len(y))
            self.assertAlmostEqual(result['precision'], tp/(tp+fp))
            self.assertAlmostEqual(result['recall'], tp/(tp+fn))
            self.assertAlmostEqual(result['f1_score'], 2*tp/(2*tp+fp+fn))
            saved, _ = read_raw_csv(ROOT / f'report/duc_predictions_{flow}.csv')
            self.assertEqual([r['y_pred'] for r in saved], list(pred))
            self.assertEqual([r['y_true'] for r in saved], list(y))

    def test_saved_cv_ranking_and_fold_scores(self):
        for flow in ('A', 'B_core', 'B'):
            rows, _ = read_raw_csv(ROOT / f'report/duc_cv_{flow}.csv')
            self.assertEqual(len(rows), 120)
            for row in rows:
                self.assertAlmostEqual(float(row['mean_test_score']), np.mean([float(row[f'split{i}_test_score']) for i in range(5)]))
            if flow != 'B_core':
                result = json.loads((ROOT / f'results/duc_decision_tree_{flow}.json').read_text(encoding='utf-8'))
                self.assertAlmostEqual(max(float(row['mean_test_score']) for row in rows), result['cv_best_f1'])

    def test_independent_sklearn_fold_loop_matches_grid_scores(self):
        # Rebuild with standard pandas/sklearn components, not TelcoPreprocessor.
        import pandas as pd
        from sklearn.compose import ColumnTransformer
        from sklearn.impute import SimpleImputer
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import OneHotEncoder
        from sklearn.tree import DecisionTreeClassifier
        from src.duc_preprocessing import B_CATEGORICAL, INTERACTIONS

        raw = pd.read_csv(DATA / 'X_train_raw.csv')
        y = load_target(DATA / 'y_train.csv')
        for flow in ('A', 'B'):
            result = json.loads((ROOT / f'results/duc_decision_tree_{flow}.json').read_text(encoding='utf-8'))
            cv_rows, _ = read_raw_csv(ROOT / f'report/duc_cv_{flow}.csv')
            wanted = {'tree__'+k: v for k, v in result['best_params'].items()}
            chosen = next(row for row in cv_rows if json.loads(row['params']) == wanted)
            frame = raw.copy()
            if flow == 'A':
                reference = joblib.load(ROOT / 'models/preprocessor_A.pkl')
            else:
                frame['MonthToMonthFiber'] = ((frame.Contract=='Month-to-month') & (frame.InternetService=='Fiber optic')).astype(int)
                frame['MonthToMonthElectronicCheck'] = ((frame.Contract=='Month-to-month') & (frame.PaymentMethod=='Electronic check')).astype(int)
                frame['RiskServiceGap'] = (frame.OnlineSecurity=='No').astype(int)+(frame.TechSupport=='No').astype(int)
                reference = ColumnTransformer([
                    ('num', SimpleImputer(strategy='median'), list(NUMERIC+INTERACTIONS)),
                    ('cat', Pipeline([('impute', SimpleImputer(strategy='most_frequent')),
                                      ('encode', OneHotEncoder(handle_unknown='ignore', sparse_output=False))]),
                     list(B_CATEGORICAL)),
                ])
            for i, (train, val) in enumerate(make_cv().split(frame, y)):
                processor = clone(reference)
                Xt = np.asarray(processor.fit_transform(frame.iloc[train]))
                Xv = np.asarray(processor.transform(frame.iloc[val]))
                tree = DecisionTreeClassifier(random_state=42, **result['best_params']).fit(Xt, y[train])
                prediction = tree.predict(Xv)
                tp = np.sum((y[val]=='Yes') & (prediction=='Yes'))
                fp = np.sum((y[val]=='No') & (prediction=='Yes'))
                fn = np.sum((y[val]=='Yes') & (prediction=='No'))
                self.assertAlmostEqual(float(chosen[f'split{i}_test_score']), 2*tp/(2*tp+fp+fn), places=12)


if __name__ == '__main__':
    unittest.main()
