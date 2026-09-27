"""
Unit tests for Boundary and Edge Case Conditions.
"""

from datetime import date
import pytest
from src.services.preprocessing_service import compute_derived_fields
from src.services.rule_engine import evaluate_claim_rules


def test_grace_period_boundary():
    """Claim filed on day 15 post-expiry (within 30-day grace) gets is_grace_period=1."""
    claim = {
        "purchase_date": "2023-01-01",
        "warranty_expiry_date": "2024-01-01",
        "claim_submission_date": "2024-01-15",
        "fault_occurrence_date": "2024-01-10",
        "missing_document_count": 0,
    }
    derived = compute_derived_fields(claim)
    assert derived["remaining_warranty_days"] == -14
    assert derived["is_grace_period"] == 1


def test_exact_expiry_day_claim():
    """Claim filed on exact day of expiry."""
    claim = {
        "purchase_date": "2023-01-01",
        "warranty_expiry_date": "2024-01-01",
        "claim_submission_date": "2024-01-01",
        "fault_occurrence_date": "2024-01-01",
        "missing_document_count": 0,
    }
    derived = compute_derived_fields(claim)
    assert derived["remaining_warranty_days"] == 0
    assert derived["warranty_active"] == "yes"