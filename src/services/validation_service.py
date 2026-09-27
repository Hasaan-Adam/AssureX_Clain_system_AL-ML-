"""Validation Service - Input Validation"""

from typing import Any, Dict, List, Optional
from datetime import date, datetime

import pandas as pd

from src.core.exceptions import ValidationError


def validate_claim_payload(claim_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate claim payload."""
    errors = []
    warnings = []
    
    # Required fields
    required = [
        "claimant_id", "product_id", "fault_occurrence_date",
        "fault_type", "claim_submission_date"
    ]
    for field in required:
        if field not in claim_data or not claim_data[field]:
            errors.append(f"Missing required field: {field}")
    
    # Date validations
    if "fault_occurrence_date" in claim_data:
        try:
            fault = pd.to_datetime(claim_data["fault_occurrence_date"]).date()
            if "claim_submission_date" in claim_data:
                submission = pd.to_datetime(claim_data["claim_submission_date"]).date()
                if fault > submission:
                    errors.append("Fault date cannot be after claim submission date")
            if "purchase_date" in claim_data:
                purchase = pd.to_datetime(claim_data["purchase_date"]).date()
                if fault < purchase:
                    errors.append("Fault date cannot be before purchase date")
        except:
            errors.append("Invalid fault_occurrence_date format")
    
    # Numeric validations
    if "purchase_price" in claim_data:
        try:
            price = float(claim_data["purchase_price"])
            if price < 0:
                errors.append("Purchase price cannot be negative")
        except:
            errors.append("Invalid purchase_price format")
    
    if "warranty_duration_months" in claim_data:
        try:
            months = int(claim_data["warranty_duration_months"])
            if months <= 0 or months > 120:
                errors.append("Warranty duration must be between 1 and 120 months")
        except:
            errors.append("Invalid warranty_duration_months format")
    
    return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}


from src.core.exceptions import ValidationError, ValidationException


def validate_claim_dates(*args, **kwargs) -> Dict[str, Any]:
    """Validate date relationships in claim (supports dict or kwargs)."""
    if args and isinstance(args[0], dict):
        claim_data = args[0]
    else:
        claim_data = kwargs

    p_date = claim_data.get("purchase_date")
    f_date = claim_data.get("fault_occurrence_date") or claim_data.get("incident_date")
    c_date = claim_data.get("claim_submission_date") or date.today()

    if p_date:
        if isinstance(p_date, str):
            p_date = pd.to_datetime(p_date).date()
        if p_date > date.today():
            raise ValidationException("Purchase date cannot be in the future")

    if f_date and p_date:
        if isinstance(f_date, str):
            f_date = pd.to_datetime(f_date).date()
        if isinstance(p_date, str):
            p_date = pd.to_datetime(p_date).date()
        if f_date < p_date:
            raise ValidationException("Fault date cannot be earlier than purchase date")

    return validate_claim_payload(claim_data)


def validate_claim_amount(*args, **kwargs) -> Dict[str, Any]:
    """Validate claim amount (supports dict or positional amount, purchase_price)."""
    if args and isinstance(args[0], (int, float)):
        amount = float(args[0])
        max_amt = float(args[1]) if len(args) > 1 and args[1] is not None else 1000000.0
        if amount < 0:
            raise ValidationException("Claim amount cannot be negative")
        if amount > max_amt:
            raise ValidationException("Claim amount cannot exceed product price")
        return {"valid": True, "errors": [], "warnings": []}
    elif args and isinstance(args[0], dict):
        claim_data = args[0]
    else:
        claim_data = kwargs

    amt = claim_data.get("claim_amount")
    if amt is not None:
        try:
            val = float(amt)
            if val < 0:
                raise ValidationException("Claim amount cannot be negative")
        except ValueError:
            raise ValidationException("Invalid claim amount format")

    return {"valid": True, "errors": [], "warnings": []}