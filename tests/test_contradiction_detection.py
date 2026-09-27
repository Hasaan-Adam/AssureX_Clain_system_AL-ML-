"""Unit tests for Contradiction Detection between Claim Payloads and Document Evidence."""

import pytest
from src.services.contradiction_service import ContradictionService, detect_contradictions, get_contradiction_service


def test_no_contradiction():
    """Verify matching payload and OCR metadata returns no contradiction."""
    claim = {"purchase_date": "2024-05-13", "purchase_price": 1000.0, "serial_number": "SN12345", "product_model": "iPhone 15"}
    extracted = {"purchase_date": "2024-05-13", "purchase_price": 1000.0, "serial_number": "SN12345", "product_model": "iPhone 15"}
    result = detect_contradictions(claim, extracted)
    assert result["has_contradiction"] is False
    assert result["confidence_penalty"] == 0.0


def test_date_and_price_contradiction():
    """Verify mismatch in purchase date (>7 days) triggers contradiction flag."""
    claim = {"purchase_date": "2024-05-01", "purchase_price": 1000.0, "serial_number": "SN12345"}
    extracted = {"purchase_date": "2024-06-01", "purchase_price": 400.0, "serial_number": "SN12345"}
    result = detect_contradictions(claim, extracted)
    assert result["has_contradiction"] is True
    assert result["confidence_penalty"] > 0.0


def test_claim_before_purchase():
    """Verify claim date before purchase date triggers hard contradiction."""
    claim = {
        "claim_submission_date": "2023-12-01",
        "purchase_date": "2024-01-15",
    }
    result = detect_contradictions(claim)
    assert result["has_contradiction"] is True
    assert result["has_hard_contradiction"] is True
    assert any(c["code"] == "claim_before_purchase" for c in result["contradictions"])
    assert result["confidence_penalty"] >= 0.35


def test_fault_after_claim():
    """Verify fault date in future after claim submission is flagged."""
    claim = {
        "claim_submission_date": "2024-06-01",
        "fault_occurrence_date": "2024-06-15",
    }
    result = detect_contradictions(claim)
    assert result["has_contradiction"] is True
    assert any(c["code"] == "fault_after_claim" for c in result["contradictions"])
    assert result["confidence_penalty"] >= 0.30


def test_repair_before_purchase():
    """Verify past repair date prior to purchase date is flagged."""
    claim = {
        "purchase_date": "2024-03-01",
        "last_repair_date": "2023-10-01",
    }
    result = detect_contradictions(claim)
    assert result["has_contradiction"] is True
    assert any(c["code"] == "repair_before_purchase" for c in result["contradictions"])
    assert result["confidence_penalty"] >= 0.30


def test_fault_before_purchase():
    """Verify fault occurrence date prior to product purchase date is flagged."""
    claim = {
        "purchase_date": "2024-05-01",
        "fault_occurrence_date": "2024-04-01",
    }
    result = detect_contradictions(claim)
    assert result["has_contradiction"] is True
    assert result["has_hard_contradiction"] is True
    assert any(c["code"] == "fault_before_purchase" for c in result["contradictions"])
    assert result["confidence_penalty"] >= 0.30


def test_model_mismatch_detection():
    """Verify mismatch between claim model and OCR extracted model is detected."""
    claim = {
        "product_model": "iPhone 15 Pro",
        "serial_number": "SN98765",
    }
    extracted = {
        "product_model": "Galaxy S23 Ultra",
        "serial_number": "SN98765",
    }
    result = detect_contradictions(claim, extracted)
    assert result["has_contradiction"] is True
    assert result["has_hard_contradiction"] is True
    assert any(c["code"] == "ocr_model_mismatch" for c in result["contradictions"])
    assert result["confidence_penalty"] >= 0.35


def test_ocr_serial_mismatch_detection():
    """Verify mismatch between claim serial number and OCR extracted serial is detected."""
    claim = {
        "serial_number": "ELC-DEL-123456",
    }
    extracted = {
        "serial_number": "ELC-HP-998877",
    }
    result = detect_contradictions(claim, extracted)
    assert result["has_contradiction"] is True
    assert result["has_hard_contradiction"] is True
    assert any(c["code"] == "ocr_serial_mismatch" for c in result["contradictions"])


def test_contradiction_service_class_instance():
    """Verify ContradictionService singleton and class wrapper methods."""
    svc = get_contradiction_service()
    claim = {"purchase_date": "2024-05-13", "purchase_price": 500.0}
    res = svc.detect(claim, claim)
    assert res["has_contradiction"] is False