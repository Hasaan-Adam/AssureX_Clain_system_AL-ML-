"""ML Feature definitions for AssureX dataset.

Usage:
    from dataset_generator.features import (
        NUMERIC_FEATURES,
        CATEGORICAL_FEATURES,
        TARGET_COLUMN,
        EXCLUDE_FROM_TRAINING,
        get_feature_columns,
    )
"""

# Columns that should NEVER be used as training features
EXCLUDE_FROM_TRAINING = {
    # Identifiers
    "claim_id",
    "product_id",
    "user_id",
    # Target / leakage
    "label",
    "scenario",
    # Dates (use derived numeric instead)
    "purchase_date",
    "warranty_start_date",
    "warranty_expiry_date",
    "claim_submission_date",
    "fault_occurrence_date",
    "last_repair_date",
    # High-cardinality or free-text
    "serial_number",
    "model_number",
    "fault_description",
    "retailer",
    "brand",
    # Redundant with derived
    "reporting_deadline_days",  # constant
    # Leakage from scenario design
    "proof_of_purchase",  # strongly predicts label
}

# Numeric features for ML pipeline (derived + original numeric)
NUMERIC_FEATURES = [
    "purchase_price",
    "warranty_duration_months",
    "product_age_days",
    "remaining_warranty_days",
    "claim_reporting_days",
    "repair_history_count",
    "missing_document_count",
]

# Categorical features for ML pipeline
CATEGORICAL_FEATURES = [
    "product_name",
    "product_category",
    "warranty_type",
    "serial_status",
    "fault_type",
    "damage_type",
    "covered_fault",
    "within_reporting_period",
    "repair_authorized",
    "previous_replacement",
    "receipt_available",
    "warranty_card_available",
    "product_image_available",
    "serial_evidence_available",
    "fault_evidence_available",
    "repair_report_available",
    "mandatory_docs_complete",
    "has_contradiction",
    "contradiction_type",
    "is_duplicate",
    "warranty_active",
    "excluded_damage",
    "ocr_quality",
]

TARGET_COLUMN = "label"
TARGET_CLASSES = ["Invalid Claim", "Manual Review", "Valid Claim"]


def get_feature_columns() -> tuple[list[str], list[str], list[str]]:
    """Return (numeric, categorical, excluded) feature column names."""
    return NUMERIC_FEATURES, CATEGORICAL_FEATURES, sorted(EXCLUDE_FROM_TRAINING)


def validate_features(df) -> None:
    """Validate that all columns are accounted for."""
    all_known = set(NUMERIC_FEATURES) | set(CATEGORICAL_FEATURES) | EXCLUDE_FROM_TRAINING | {TARGET_COLUMN}
    missing = set(df.columns) - all_known
    extra = all_known - set(df.columns)
    if missing:
        raise ValueError(f"Columns not in feature lists: {missing}")
    if extra - {"scenario", "product_id", "user_id", "claim_id"}:
        raise ValueError(f"Feature list has columns not in data: {extra}")