"""Unit and integration tests for the Python ML Model Pipeline."""

from pathlib import Path
import pandas as pd
import pytest

from src.ml.evaluate import evaluate_model
from src.ml.predict import ClaimPredictor, batch_predict_claims, predict_claim


def test_predict_claim_interface():
    """Verify single prediction output structure and schema."""
    sample_claim = {
        "claim_id": "CLM-TEST-001",
        "product_name": "Laptop",
        "product_category": "electronics",
        "brand": "Dell",
        "model_number": "DE926-ELE",
        "serial_number": "ELC-DEL-984830",
        "serial_status": "match",
        "purchase_date": "2024-05-13",
        "purchase_price": 308176,
        "retailer": "City Mart Stores",
        "warranty_duration_months": 36,
        "warranty_type": "standard",
        "warranty_start_date": "2024-05-13",
        "warranty_expiry_date": "2027-05-13",
        "claim_submission_date": "2024-10-15",
        "product_age_days": 155,
        "remaining_warranty_days": 940,
        "fault_occurrence_date": "2024-10-10",
        "fault_type": "battery_degradation",
        "fault_description": "Intermittent fault observed",
        "damage_type": "manufacturing_defect",
        "covered_fault": "yes",
        "claim_reporting_days": 5,
        "within_reporting_period": "yes",
        "reporting_deadline_days": 30,
        "repair_history_count": 0,
        "repair_authorized": "none",
        "previous_replacement": "no",
        "receipt_available": "yes",
        "warranty_card_available": "yes",
        "product_image_available": "yes",
        "serial_evidence_available": "yes",
        "fault_evidence_available": "yes",
        "repair_report_available": "no",
        "missing_document_count": 1,
        "mandatory_docs_complete": "yes",
        "has_contradiction": "no",
        "contradiction_type": "none",
        "is_duplicate": "no",
        "proof_of_purchase": "yes",
        "warranty_active": "yes",
        "excluded_damage": "no",
        "ocr_quality": "high",
    }

    result = predict_claim(sample_claim)

    assert isinstance(result, dict)
    assert "predicted_class" in result
    assert "confidence" in result
    assert "probabilities" in result
    assert "model_version" in result

    assert result["predicted_class"] in ["Valid Claim", "Invalid Claim", "Manual Review"]
    assert 0.0 <= result["confidence"] <= 1.0
    assert isinstance(result["probabilities"], dict)
    assert len(result["probabilities"]) == 3
    assert abs(sum(result["probabilities"].values()) - 1.0) < 1e-2


def test_batch_predict_claims():
    """Verify batch prediction on test records."""
    test_df = pd.read_csv("data/test/claims_test.csv")
    samples = test_df.head(10).to_dict(orient="records")

    results = batch_predict_claims(samples)

    assert len(results) == 10
    for res in results:
        assert res["predicted_class"] in ["Valid Claim", "Invalid Claim", "Manual Review"]
        assert 0.0 <= res["confidence"] <= 1.0


def test_model_srs_accuracy_requirement():
    """Verify that model achieves >= 85% accuracy on the test set (SRS Requirement)."""
    report = evaluate_model(test_csv=Path("data/test/claims_test.csv"))

    assert report["srs_requirement_met"] is True
    assert report["metrics"]["accuracy"] >= 0.85
    assert report["metrics"]["f1_macro"] >= 0.85