"""Unit tests for Duplicate Claim Submissions Detection."""

import pytest
from src.models.claim import Claim
from src.services.duplicate_service import (
    check_duplicate_claim,
    check_duplicate_document,
)


from datetime import date

def test_duplicate_claim_detection(test_db, customer_user, sample_warranty):
    """Test detecting repeated claim on same warranty."""
    claim1 = Claim(
        claim_number="CLM-DUP-1",
        user_id=customer_user.id,
        product_id=sample_warranty.product_id,
        warranty_id=sample_warranty.id,
        fault_occurrence_date=date.today(),
        fault_type="Screen Glitch",
        description="Flickering LCD display",
        claim_amount=150.0,
    )
    test_db.add(claim1)
    test_db.commit()

    dup_res = check_duplicate_claim(test_db, warranty_id=sample_warranty.id, fault_type="Screen Glitch")
    assert dup_res["is_duplicate"] is True
    assert dup_res["duplicate_count"] >= 1
    assert "CLM-DUP-1" in dup_res["matching_claim_numbers"]


def test_duplicate_claim_in_memory_history():
    """Test in-memory claim history duplication detection."""
    claim = {
        "claim_id": "CLM-NEW-01",
        "user_id": "USR-100",
        "serial_number": "SN-DELL-9988",
        "fault_type": "POWER_FAILURE",
        "claim_submission_date": "2024-06-01",
    }
    history = [
        {
            "claim_id": "CLM-OLD-01",
            "user_id": "USR-100",
            "serial_number": "SN-DELL-9988",
            "fault_type": "POWER_FAILURE",
            "claim_submission_date": "2024-05-20",
        }
    ]
    res = check_duplicate_claim(claim, claim_history=history)
    assert res["is_duplicate"] is True
    assert "CLM-OLD-01" in res["matching_claim_numbers"]


def test_duplicate_document_checksum():
    """Test detecting reused document hash."""
    file_hash = "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
    res = check_duplicate_document(file_hash, existing_hashes=[file_hash])
    assert res["is_duplicate"] is True
    assert res["duplicate_type"] == "DOCUMENT_HASH_MATCH"