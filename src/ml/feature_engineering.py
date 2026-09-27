"""Feature Engineering Module for AssureX Claim Engine.

Extracts, cleans, and constructs tabular features from raw claim dictionaries or DataFrames.
Handles missing data, date calculations, boolean flag parsing, and domain-specific feature derivation.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Sequence, Union
import numpy as np
import pandas as pd


# Feature Column Definitions
NUMERIC_FEATURES: List[str] = [
    "product_age_days",
    "remaining_warranty_days",
    "warranty_duration_months",
    "purchase_price",
    "claim_reporting_days",
    "reporting_deadline_days",
    "repair_history_count",
    "missing_document_count",
    "price_per_month",
    "days_past_expiry",
    "is_grace_period",
    "is_reporting_overdue",
    "repair_frequency",
]

BOOLEAN_FEATURES: List[str] = [
    "covered_fault",
    "within_reporting_period",
    "previous_replacement",
    "receipt_available",
    "warranty_card_available",
    "product_image_available",
    "serial_evidence_available",
    "fault_evidence_available",
    "repair_report_available",
    "mandatory_docs_complete",
    "has_contradiction",
    "is_duplicate",
    "proof_of_purchase",
    "warranty_active",
    "excluded_damage",
]

CATEGORICAL_FEATURES: List[str] = [
    "product_category",
    "product_name",
    "brand",
    "serial_status",
    "retailer",
    "warranty_type",
    "fault_type",
    "damage_type",
    "repair_authorized",
    "contradiction_type",
    "ocr_quality",
]

DOCUMENT_FLAG_COLUMNS: List[str] = [
    "receipt_available",
    "warranty_card_available",
    "product_image_available",
    "serial_evidence_available",
    "fault_evidence_available",
    "repair_report_available",
]

TARGET_COLUMN: str = "label"

# Default feature column order
FEATURE_COLUMNS: List[str] = NUMERIC_FEATURES + BOOLEAN_FEATURES + CATEGORICAL_FEATURES


def parse_boolean(value: Any) -> int:
    """Safely converts various boolean representations into integer 0 or 1.
    
    Supports: bool, int, float, and strings ('yes', 'no', 'true', 'false', '1', '0', etc.)
    """
    if value is None or pd.isna(value):
        return 0
    if isinstance(value, (bool, np.bool_)):
        return 1 if value else 0
    if isinstance(value, (int, float, np.integer, np.floating)):
        return 1 if value > 0 else 0
    
    str_val = str(value).strip().lower()
    if str_val in ("yes", "true", "1", "t", "y", "match", "authorized"):
        return 1
    return 0


def parse_date_value(val: Any) -> Union[datetime, None]:
    """Parse various date formats or strings into datetime object."""
    if val is None or pd.isna(val):
        return None
    if isinstance(val, (datetime, pd.Timestamp)):
        return val
    if isinstance(val, date):
        return datetime.combine(val, datetime.min.time())
    
    str_val = str(val).strip()
    if not str_val or str_val.lower() in ("nan", "none", "null", "nat"):
        return None
    
    try:
        return pd.to_datetime(str_val)
    except Exception:
        return None


def calculate_days_between(d1: Any, d2: Any) -> Union[int, None]:
    """Calculates days difference: (d1 - d2). Returns None if either is missing."""
    dt1 = parse_date_value(d1)
    dt2 = parse_date_value(d2)
    if dt1 is None or dt2 is None:
        return None
    return int((dt1 - dt2).total_seconds() / 86400)


def extract_features(
    data: Union[Dict[str, Any], Sequence[Dict[str, Any]], pd.DataFrame]
) -> pd.DataFrame:
    """Extracts, cleans, and engineers features from raw claim dictionary or DataFrame.
    
    Args:
        data: Single claim dict, list of claim dicts, or pandas DataFrame.
        
    Returns:
        pd.DataFrame containing engineered feature columns ready for preprocessing.
    """
    # Convert input to DataFrame
    if isinstance(data, dict):
        df = pd.DataFrame([data])
    elif isinstance(data, list):
        df = pd.DataFrame(data)
    elif isinstance(data, pd.DataFrame):
        df = data.copy()
    else:
        raise TypeError(f"Unsupported data type for feature extraction: {type(data)}")

    result = pd.DataFrame(index=df.index)

    # 1. Date Arithmetic & Derived Timelines
    # Product Age Days
    if "product_age_days" in df.columns and not df["product_age_days"].isnull().all():
        result["product_age_days"] = pd.to_numeric(df["product_age_days"], errors="coerce").fillna(0)
    else:
        # Calculate from claim_submission_date - purchase_date
        sub_dates = pd.to_datetime(df.get("claim_submission_date"), errors="coerce")
        pur_dates = pd.to_datetime(df.get("purchase_date"), errors="coerce")
        result["product_age_days"] = (sub_dates - pur_dates).dt.days.fillna(0).clip(lower=0)

    # Remaining Warranty Days
    if "remaining_warranty_days" in df.columns and not df["remaining_warranty_days"].isnull().all():
        result["remaining_warranty_days"] = pd.to_numeric(df["remaining_warranty_days"], errors="coerce").fillna(0)
    else:
        # Calculate from warranty_expiry_date - claim_submission_date
        exp_dates = pd.to_datetime(df.get("warranty_expiry_date"), errors="coerce")
        sub_dates = pd.to_datetime(df.get("claim_submission_date"), errors="coerce")
        result["remaining_warranty_days"] = (exp_dates - sub_dates).dt.days.fillna(0)

    # Claim Reporting Days
    if "claim_reporting_days" in df.columns and not df["claim_reporting_days"].isnull().all():
        result["claim_reporting_days"] = pd.to_numeric(df["claim_reporting_days"], errors="coerce").fillna(0)
    else:
        # Calculate from claim_submission_date - fault_occurrence_date
        sub_dates = pd.to_datetime(df.get("claim_submission_date"), errors="coerce")
        flt_dates = pd.to_datetime(df.get("fault_occurrence_date"), errors="coerce")
        result["claim_reporting_days"] = (sub_dates - flt_dates).dt.days.fillna(0).clip(lower=0)

    # Warranty Duration Months
    if "warranty_duration_months" in df.columns:
        result["warranty_duration_months"] = pd.to_numeric(df["warranty_duration_months"], errors="coerce").fillna(12)
    else:
        result["warranty_duration_months"] = 12

    # Purchase Price
    if "purchase_price" in df.columns:
        result["purchase_price"] = pd.to_numeric(df["purchase_price"], errors="coerce").fillna(0)
    else:
        result["purchase_price"] = 0

    # Reporting Deadline Days (standard is 30 days)
    if "reporting_deadline_days" in df.columns:
        result["reporting_deadline_days"] = pd.to_numeric(df["reporting_deadline_days"], errors="coerce").fillna(30)
    else:
        result["reporting_deadline_days"] = 30

    # Repair History Count
    if "repair_history_count" in df.columns:
        result["repair_history_count"] = pd.to_numeric(df["repair_history_count"], errors="coerce").fillna(0)
    else:
        result["repair_history_count"] = 0

    # 2. Boolean Features Conversion
    for col in BOOLEAN_FEATURES:
        if col in df.columns:
            result[col] = df[col].apply(parse_boolean)
        else:
            result[col] = 0

    # 3. Missing Document Count (compute if missing)
    if "missing_document_count" in df.columns and not df["missing_document_count"].isnull().all():
        result["missing_document_count"] = pd.to_numeric(df["missing_document_count"], errors="coerce").fillna(0)
    else:
        # Count available docs
        avail_docs = sum(result[col] for col in DOCUMENT_FLAG_COLUMNS if col in result.columns)
        result["missing_document_count"] = (len(DOCUMENT_FLAG_COLUMNS) - avail_docs).clip(lower=0)

    # 4. Domain Feature Engineering
    # Price per month of warranty
    result["price_per_month"] = result["purchase_price"] / np.maximum(result["warranty_duration_months"], 1)

    # Days past expiry (0 if still active)
    result["days_past_expiry"] = np.maximum(0, -result["remaining_warranty_days"])

    # Grace period indicator (-15 <= remaining_warranty_days < 0)
    result["is_grace_period"] = (
        (result["remaining_warranty_days"] >= -15) & (result["remaining_warranty_days"] < 0)
    ).astype(int)

    # Reporting overdue indicator
    result["is_reporting_overdue"] = (
        result["claim_reporting_days"] > result["reporting_deadline_days"]
    ).astype(int)

    # Repair frequency relative to product age (in years)
    age_in_years = (result["product_age_days"] / 365.25).clip(lower=0.01)
    result["repair_frequency"] = result["repair_history_count"] / age_in_years

    # 5. Categorical Features Handling
    for col in CATEGORICAL_FEATURES:
        if col in df.columns:
            result[col] = df[col].fillna("missing").astype(str).str.strip().str.lower()
        else:
            result[col] = "missing"

    # Ensure all target FEATURE_COLUMNS are present in strict order
    for col in FEATURE_COLUMNS:
        if col not in result.columns:
            result[col] = 0

    return result[FEATURE_COLUMNS]


def extract_features_and_target(
    df: pd.DataFrame, target_column: str = TARGET_COLUMN
) -> tuple[pd.DataFrame, pd.Series]:
    """Extracts features DataFrame X and target Series y from input DataFrame.
    
    Args:
        df: Input DataFrame containing claim records and target column.
        target_column: Column name for label (default 'label').
        
    Returns:
        Tuple of (X, y).
    """
    if target_column not in df.columns:
        raise ValueError(f"Target column '{target_column}' not found in DataFrame.")
    
    X = extract_features(df)
    y = df[target_column].astype(str).str.strip()
    return X, y