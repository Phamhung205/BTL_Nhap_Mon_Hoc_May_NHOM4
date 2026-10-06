"""Cloneable transformers with fold-local state and stable pickle import paths.

Input: raw CSV row dictionaries. Output: finite numerical NumPy matrix in the
same row order. A reproduces Manh's recipe; B uses a fixed EDA feature set.
"""
from __future__ import annotations

import math
from collections import Counter

import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import StandardScaler
from sklearn.utils.validation import check_is_fitted

NUMERIC = ("SeniorCitizen", "tenure", "MonthlyCharges", "TotalCharges")
CATEGORICAL = (
    "gender", "Partner", "Dependents", "PhoneService", "MultipleLines",
    "InternetService", "OnlineSecurity", "OnlineBackup", "DeviceProtection",
    "TechSupport", "StreamingTV", "StreamingMovies", "Contract",
    "PaperlessBilling", "PaymentMethod",
)
B_CATEGORICAL = (
    "Partner", "Dependents", "InternetService", "OnlineSecurity", "TechSupport",
    "Contract", "PaperlessBilling", "PaymentMethod",
)
INTERACTIONS = ("MonthToMonthFiber", "MonthToMonthElectronicCheck", "RiskServiceGap")


def number(value):
    """Blank/NaN is missing; malformed or infinite numbers are rejected."""
    if value is None or not str(value).strip():
        return np.nan
    try:
        result = float(value)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"Invalid numeric value: {value!r}") from exc
    if math.isinf(result):
        raise ValueError("Infinite input is not supported.")
    return result


def category(value):
    return "" if value is None else str(value).strip()


class TelcoPreprocessor(TransformerMixin, BaseEstimator):
    """B_core is a Train-only ablation, not a replacement final flow.

    Unknown levels have an all-zero one-hot block, like handle_unknown=ignore.
    """

    def __init__(self, flow="B"):
        self.flow = flow

    def _validate(self, rows):
        if self.flow not in ("A", "B", "B_core"):
            raise ValueError(f"Unknown flow: {self.flow}")
        if len(rows) == 0:
            raise ValueError("Empty input.")
        required = set(NUMERIC + CATEGORICAL)
        for index, row in enumerate(rows):
            if not isinstance(row, dict) or not required.issubset(row):
                raise ValueError(f"Raw row {index} is missing required columns.")

    def fit(self, X, y=None):
        self._validate(X)
        self.categorical_columns_ = CATEGORICAL if self.flow == "A" else B_CATEGORICAL
        self.numeric_medians_ = {}
        for column in NUMERIC:
            values = np.array([number(row[column]) for row in X])
            if np.isnan(values).all():
                raise ValueError(f"All training values missing: {column}")
            self.numeric_medians_[column] = float(np.nanmedian(values))
        self.categorical_modes_ = {}
        self.categorical_levels_ = {}
        for column in self.categorical_columns_:
            counts = Counter(category(row[column]) for row in X if category(row[column]))
            if not counts:
                raise ValueError(f"All training values missing: {column}")
            self.categorical_modes_[column] = min(counts, key=lambda x: (-counts[x], x))
            self.categorical_levels_[column] = sorted(counts)
        self.scaler_ = StandardScaler().fit(self._numeric(X)) if self.flow == "A" else None
        names = [f"num__{c}" for c in NUMERIC] if self.flow == "A" else list(NUMERIC)
        if self.flow == "B":
            names.extend(INTERACTIONS)
        for column in self.categorical_columns_:
            names.extend(
                f"cat__{column}_{level}" if self.flow == "A" else f"{column}__{level}"
                for level in self.categorical_levels_[column]
            )
        self.feature_names_ = names
        return self

    def _numeric(self, X):
        values = np.array([[number(row[c]) for c in NUMERIC] for row in X], dtype=float)
        return np.where(np.isnan(values), [self.numeric_medians_[c] for c in NUMERIC], values)

    def transform(self, X):
        check_is_fitted(self, "feature_names_")
        self._validate(X)
        numeric = self._numeric(X)
        if self.scaler_ is not None:
            numeric = self.scaler_.transform(numeric)
        categories = {
            c: np.array([category(row[c]) or self.categorical_modes_[c] for row in X])
            for c in self.categorical_columns_
        }
        blocks = [numeric]
        if self.flow == "B":
            monthly = categories["Contract"] == "Month-to-month"
            blocks.append(np.column_stack([
                monthly & (categories["InternetService"] == "Fiber optic"),
                monthly & (categories["PaymentMethod"] == "Electronic check"),
                (categories["OnlineSecurity"] == "No").astype(int)
                + (categories["TechSupport"] == "No").astype(int),
            ]))
        for column in self.categorical_columns_:
            blocks.append(np.column_stack([
                categories[column] == level for level in self.categorical_levels_[column]
            ]))
        result = np.column_stack(blocks).astype(float)
        if not np.isfinite(result).all():
            raise ValueError("Non-finite transformed value.")
        return result

    def get_feature_names_out(self, input_features=None):
        check_is_fitted(self, "feature_names_")
        return np.asarray(self.feature_names_, dtype=object)


class FeatureEngineerB(TelcoPreprocessor):
    """Stable import path for B artifacts created by CLI or notebook."""

    def __init__(self):
        super().__init__(flow="B")
