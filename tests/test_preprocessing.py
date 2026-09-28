"""Unit tests for Feature Engineering and Preprocessing Pipeline."""

import numpy as np
import pandas as pd
import pytest
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import LabelEncoder

from src.ml.feature_engineering import (
    FEATURE_COLUMNS,
    calculate_days_between,
    extract_features,
    extract_features_and_target,
    parse_boolean,
    parse_date_value,
)
from src.ml.preprocess_pipeline import (
    build_label_encoder,
    build_preprocessor,
    load_label_encoder,
    load_preprocessor,
    save_label_encoder,
    save_preprocessor,
)


def test_parse_boolean():
    """Verify robust parsing of various boolean representations."""
    assert parse_boolean(True) == 1
    assert parse_boolean(False) == 0
    assert parse_boolean(1) == 1
    assert parse_boolean(0) == 0
    assert parse_boolean("yes") == 1
    assert parse_boolean("YES") == 1
    assert parse_boolean("true") == 1
    assert parse_boolean("no") == 0
    assert parse_boolean("false") == 0
    assert parse_boolean("0") == 0
    assert parse_boolean(None) == 0
    assert parse_boolean(np.nan) == 0


def test_calculate_days_between():
    """Verify date difference calculation in days."""
    assert calculate_days_between("2024-05-20", "2024-05-10") == 10
    assert calculate_days_between("2024-05-10", "2024-05-20") == -10
    assert calculate_days_between(None, "2024-05-10") is None
    assert calculate_days_between("invalid-date", "2024-05-10") is None


def test_extract_features_from_dict():
    """Test feature extraction on a single raw claim dictionary."""
    claim = {
        "purchase_date": "2024-01-01",
        "warranty_expiry_date": "2025-01-01",
        "claim_submission_date": "2024-06-01",
        "fault_occurrence_date": "2024-05-25",
        "purchase_price": 50000,
        "warranty_duration_months": 12,
        "covered_fault": "yes",
        "receipt_available": "yes",
        "warranty_card_available": "yes",
        "product_image_available": "yes",
        "serial_evidence_available": "yes",
        "fault_evidence_available": "yes",
        "repair_report_available": "no",
        "product_category": "electronics",
        "product_name": "Laptop",
        "brand": "Dell",
        "serial_status": "match",
    }

    df = extract_features(claim)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert all(col in df.columns for col in FEATURE_COLUMNS)
    assert df["product_age_days"].iloc[0] == 152
    assert df["remaining_warranty_days"].iloc[0] == 214
    assert df["claim_reporting_days"].iloc[0] == 7
    assert df["missing_document_count"].iloc[0] == 1
    assert df["covered_fault"].iloc[0] == 1
    assert df["is_grace_period"].iloc[0] == 0


def test_extract_features_and_target():
    """Test feature and target separation from DataFrame."""
    data = {
        "purchase_date": ["2024-01-01", "2024-02-01"],
        "warranty_expiry_date": ["2025-01-01", "2025-02-01"],
        "claim_submission_date": ["2024-06-01", "2024-06-01"],
        "fault_occurrence_date": ["2024-05-25", "2024-05-25"],
        "purchase_price": [50000, 75000],
        "warranty_duration_months": [12, 12],
        "label": ["Valid Claim", "Invalid Claim"],
    }
    df = pd.DataFrame(data)
    X, y = extract_features_and_target(df, target_column="label")
    assert len(X) == 2
    assert len(y) == 2
    assert list(y) == ["Valid Claim", "Invalid Claim"]


def test_preprocessor_pipeline(tmp_path):
    """Test building, fitting, saving, and loading ColumnTransformer and LabelEncoder."""
    data = {
        "purchase_date": ["2024-01-01", "2024-02-01", "2023-01-01"],
        "warranty_expiry_date": ["2025-01-01", "2025-02-01", "2024-01-01"],
        "claim_submission_date": ["2024-06-01", "2024-06-01", "2024-06-01"],
        "fault_occurrence_date": ["2024-05-25", "2024-05-25", "2024-05-25"],
        "purchase_price": [50000, 75000, 20000],
        "warranty_duration_months": [12, 12, 12],
        "product_category": ["electronics", "mobile_phones", "home_appliances"],
        "product_name": ["Laptop", "Smartphone", "Refrigerator"],
        "brand": ["Dell", "Samsung", "Haier"],
        "serial_status": ["match", "match", "mismatch"],
        "label": ["Valid Claim", "Valid Claim", "Invalid Claim"],
    }
    df = pd.DataFrame(data)
    X, y = extract_features_and_target(df)

    preprocessor = build_preprocessor()
    label_encoder = build_label_encoder()

    X_trans = preprocessor.fit_transform(X)
    y_enc = label_encoder.fit_transform(y)

    assert X_trans.shape[0] == 3
    assert len(y_enc) == 3

    prep_path = tmp_path / "preprocessor.joblib"
    le_path = tmp_path / "label_encoder.joblib"

    save_preprocessor(preprocessor, prep_path)
    save_label_encoder(label_encoder, le_path)

    loaded_prep = load_preprocessor(prep_path)
    loaded_le = load_label_encoder(le_path)

    X_trans_loaded = loaded_prep.transform(X)
    y_enc_loaded = loaded_le.transform(y)

    np.testing.assert_array_almost_equal(X_trans, X_trans_loaded)
    np.testing.assert_array_equal(y_enc, y_enc_loaded)