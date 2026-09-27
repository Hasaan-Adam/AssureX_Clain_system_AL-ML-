"""Preprocessing Service - Feature Engineering"""

from typing import Any, Dict, List, Optional
import pandas as pd
import numpy as np
from datetime import date, datetime


def compute_derived_fields(claim_data: Dict[str, Any]) -> Dict[str, Any]:
    """Compute all derived fields for a claim."""
    result = dict(claim_data)
    
    # Product age
    if "purchase_date" in claim_data and "claim_submission_date" in claim_data:
        try:
            purchase = pd.to_datetime(claim_data["purchase_date"])
            submission = pd.to_datetime(claim_data["claim_submission_date"])
            result["product_age_days"] = (submission - purchase).days
        except:
            result["product_age_days"] = 0
    
    # Remaining warranty
    if "warranty_expiry_date" in claim_data and "claim_submission_date" in claim_data:
        try:
            expiry = pd.to_datetime(claim_data["warranty_expiry_date"])
            submission = pd.to_datetime(claim_data["claim_submission_date"])
            result["remaining_warranty_days"] = (expiry - submission).days
        except:
            result["remaining_warranty_days"] = 0
    
    # Claim reporting days
    if "fault_occurrence_date" in claim_data and "claim_submission_date" in claim_data:
        try:
            fault = pd.to_datetime(claim_data["fault_occurrence_date"])
            submission = pd.to_datetime(claim_data["claim_submission_date"])
            result["claim_reporting_days"] = max(0, (submission - fault).days)
        except:
            result["claim_reporting_days"] = 0
    
    # Within reporting period
    result["within_reporting_period"] = "yes" if result.get("claim_reporting_days", 0) <= 30 else "no"
    
    # Remaining warranty days
    rem = result.get("remaining_warranty_days", 0)
    
    # Warranty active (string yes/no)
    result["warranty_active"] = "yes" if rem >= 0 else "no"
    
    # Days past expiry
    result["days_past_expiry"] = max(0, -rem)
    
    # Grace period (integer flag 1/0)
    result["is_grace_period"] = 1 if -30 <= rem < 0 else 0
    
    # Reporting overdue (integer flag 1/0)
    result["is_reporting_overdue"] = 1 if result.get("claim_reporting_days", 0) > 30 else 0
    
    # Repair frequency
    if "product_age_days" in result and result["product_age_days"] > 0:
        repair_count = claim_data.get("repair_history_count", 0)
        age_years = max(result["product_age_days"] / 365.25, 0.01)
        result["repair_frequency"] = repair_count / age_years
    else:
        result["repair_frequency"] = 0
    
    # Price per month
    if "purchase_price" in claim_data and "warranty_duration_months" in claim_data:
        months = max(claim_data.get("warranty_duration_months", 1), 1)
        result["price_per_month"] = claim_data["purchase_price"] / months
    else:
        result["price_per_month"] = 0
    
    return result


def prepare_features_for_ml(claim_data: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare features for ML model."""
    enriched = compute_derived_fields(claim_data)
    
    # Boolean features
    boolean_map = {
        "covered_fault": "yes",
        "within_reporting_period": "yes",
        "previous_replacement": "yes",
        "receipt_available": "yes",
        "warranty_card_available": "yes",
        "product_image_available": "yes",
        "serial_evidence_available": "yes",
        "fault_evidence_available": "yes",
        "repair_report_available": "yes",
        "mandatory_docs_complete": "yes",
        "has_contradiction": "yes",
        "is_duplicate": "yes",
        "proof_of_purchase": "yes",
        "warranty_active": "yes",
        "excluded_damage": "yes",
    }
    
    for key, pos_val in boolean_map.items():
        if key in enriched:
            enriched[key] = 1 if str(enriched[key]).lower() in (pos_val, "true", "1", "yes") else 0
    
    return enriched


def prepare_batch_features(claims: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [prepare_features_for_ml(c) for c in claims]