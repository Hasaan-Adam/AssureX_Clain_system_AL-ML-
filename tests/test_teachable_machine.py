"""
Unit tests for Teachable Machine integration and visual claim classification.
"""

import pytest
from src.services.tm_service import predict_visual_claim


def test_visual_claim_prediction():
    """Verify Teachable Machine visual claim classification output format."""
    res = predict_visual_claim()
    assert "model_name" in res
    assert "predicted_label" in res
    assert "confidence" in res
    assert "probabilities" in res
    assert res["confidence"] > 0.0
    assert "Valid Claim" in res["probabilities"]
    assert "Invalid Claim" in res["probabilities"]
    assert "Manual Review" in res["probabilities"]


def test_claim_card_prediction_valid():
    """Verify Teachable Machine prediction for valid claim summary card."""
    from src.services.tm_service import predict_claim_card
    claim_data = {
        "covered_fault": "yes",
        "warranty_active": "yes",
        "claim_amount": 150.0,
    }
    res = predict_claim_card(claim_data)
    assert res["predicted_label"] == "Valid Claim"
    assert res["predicted_class"] == "Valid Claim"
    assert res["confidence"] >= 0.80
    assert res["probabilities"]["Valid Claim"] > 0.80


def test_claim_card_prediction_invalid():
    """Verify Teachable Machine prediction for invalid claim summary card (e.g. inactive warranty)."""
    from src.services.tm_service import predict_claim_card
    claim_data = {
        "covered_fault": "no",
        "warranty_active": "no",
        "claim_amount": 500.0,
    }
    res = predict_claim_card(claim_data)
    assert res["predicted_label"] == "Invalid Claim"
    assert res["predicted_class"] == "Invalid Claim"
    assert res["confidence"] >= 0.90
    assert res["probabilities"]["Invalid Claim"] > 0.85