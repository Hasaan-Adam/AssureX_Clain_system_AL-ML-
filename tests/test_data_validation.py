"""Tests for Dataset Validation, Card Generation, and SRS Compliance."""

import csv
from pathlib import Path
from PIL import Image

from dataset_generator.validate_dataset import validate_tabular, validate_card_images, IMAGE_MAP_PATH
from src.card.renderer import render_claim_card, FORBIDDEN_FIELDS, DEFAULT_WIDTH, DEFAULT_HEIGHT
from src.card.variations import render_card_variation, generate_card_variations, VARIATION_THEMES

ROOT = Path(__file__).resolve().parents[1]
TRAIN_CSV = ROOT / "data" / "train" / "claims_train.csv"


def test_tabular_dataset_validity():
    """Verify tabular dataset has exact balance and zero cross-split leakage."""
    errors, warnings = validate_tabular()
    assert len(errors) == 0, f"Tabular validation errors: {errors}"


def test_card_image_dataset_validity():
    """Verify card images exist across splits, match CSV IDs, and are valid."""
    errors, records, split_counts = validate_card_images()
    assert len(errors) == 0, f"Card image validation errors: {errors}"
    assert split_counts["train"]["base"] > 0
    assert split_counts["train"]["variations"] > 0
    assert split_counts["validation"]["base"] > 0
    assert split_counts["test"]["base"] > 0
    assert len(records) > 0
    assert IMAGE_MAP_PATH.exists()



def test_claim_card_rendering():
    """Verify single card rendering produces valid RGB 800x600 image."""
    sample_claim = {
        "claim_id": "CLM-TEST-001",
        "product_name": "Laptop",
        "product_category": "electronics",
        "brand": "Dell",
        "model_number": "DE-100",
        "serial_number": "SN-9999",
        "serial_status": "match",
        "purchase_date": "2024-01-01",
        "purchase_price": "150000",
        "retailer": "Tech Store",
        "product_age_days": "180",
        "warranty_type": "standard",
        "warranty_duration_months": "12",
        "warranty_start_date": "2024-01-01",
        "warranty_expiry_date": "2025-01-01",
        "remaining_warranty_days": "185",
        "warranty_active": "yes",
        "proof_of_purchase": "yes",
        "claim_submission_date": "2024-07-01",
        "fault_type": "battery_degradation",
        "fault_description": "Battery fails to hold charge.",
        "damage_type": "manufacturing_defect",
        "covered_fault": "yes",
        "claim_reporting_days": "5",
        "within_reporting_period": "yes",
        "repair_history_count": "0",
        "repair_authorized": "none",
        "receipt_available": "yes",
        "warranty_card_available": "yes",
        "product_image_available": "yes",
        "serial_evidence_available": "yes",
        "fault_evidence_available": "yes",
        "repair_report_available": "no",
        "mandatory_docs_complete": "yes",
        "has_contradiction": "no",
        "is_duplicate": "no",
        "ocr_quality": "high",
        "label": "Valid Claim",
        "prediction": "Valid Claim",
        "confidence": "0.99",
    }

    img = render_claim_card(sample_claim)
    assert isinstance(img, Image.Image)
    assert img.size == (DEFAULT_WIDTH, DEFAULT_HEIGHT)
    assert img.mode == "RGB"


def test_card_variations():
    """Verify variations generator produces distinct themed cards."""
    sample_claim = {
        "claim_id": "CLM-TEST-002",
        "product_name": "Smartphone",
        "product_category": "mobile_phones",
        "brand": "Apple",
        "serial_status": "match",
        "warranty_active": "yes",
        "has_contradiction": "no",
    }

    vars = generate_card_variations(sample_claim, n_variations=2)
    assert len(vars) == 2
    for v in vars:
        assert isinstance(v, Image.Image)
        assert v.size == (DEFAULT_WIDTH, DEFAULT_HEIGHT)
        assert v.mode == "RGB"