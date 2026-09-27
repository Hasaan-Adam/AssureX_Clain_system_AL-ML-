"""
Unit tests for Negative Validation and Error Scenarios.
"""

from datetime import date, timedelta
import pytest
from src.core.exceptions import ValidationException
from src.services.validation_service import validate_claim_amount, validate_claim_dates


def test_negative_claim_amount():
    """Negative claim amount raises ValidationException."""
    with pytest.raises(ValidationException):
        validate_claim_amount(-50.0, 500.0)


def test_future_purchase_date():
    """Future purchase date raises ValidationException."""
    future_date = date.today() + timedelta(days=5)
    with pytest.raises(ValidationException):
        validate_claim_dates(purchase_date=future_date)


def test_fault_before_purchase():
    """Fault date earlier than purchase date raises ValidationException."""
    p_date = date(2024, 5, 10)
    f_date = date(2024, 4, 1)
    with pytest.raises(ValidationException):
        validate_claim_dates(purchase_date=p_date, fault_occurrence_date=f_date)