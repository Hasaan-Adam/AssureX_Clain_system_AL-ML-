"""Unit tests for Missing Documents Validation by Product Category."""

import pytest
from src.services.missing_doc_service import check_missing_documents


def test_complete_documents():
    """Verify all required docs present (legacy UI vocabulary is normalised)."""
    docs = ["purchase_invoice", "serial_number_photo", "damage_photo"]
    res = check_missing_documents(category="ELECTRONICS", available_doc_types=docs)
    assert res["is_complete"] is True
    assert res["missing_count"] == 0
    assert res["completeness_score"] == 1.0
    assert res["action_needed"] == "PROCEED"
    assert set(res["available_documents"]) == {"receipt", "serial_evidence", "fault_evidence"}


def test_missing_documents():
    """Verify missing damage photo is reported against the required bundle."""
    docs = ["purchase_invoice"]
    res = check_missing_documents(category="ELECTRONICS", available_doc_types=docs)
    assert res["is_complete"] is False
    assert "fault_evidence" in res["missing_documents"]
    assert "serial_evidence" in res["missing_documents"]
    assert res["missing_count"] >= 1
    assert res["action_needed"] == "REQUEST_DOCUMENTS"
    assert res["completeness_score"] < 1.0


def test_missing_documents_claim_dict_evaluation():
    """Verify evaluation on full claim dictionary with missing receipt."""
    claim = {
        "product_category": "electronics",
        "receipt_available": "no",
        "warranty_card_available": "yes",
        "serial_evidence_available": "yes",
        "fault_evidence_available": "yes",
        "repair_history_count": 0,
    }
    res = check_missing_documents(claim=claim)
    assert res["is_complete"] is False
    assert "receipt" in res["missing_mandatory_docs"]
    assert res["action_needed"] == "REQUEST_DOCUMENTS"
    assert res["mandatory_docs_complete"] is False


def test_repair_report_required_when_repairs_present():
    """Verify repair report is mandatory when prior repairs exist."""
    claim = {
        "product_category": "electronics",
        "receipt_available": "yes",
        "warranty_card_available": "yes",
        "serial_evidence_available": "yes",
        "fault_evidence_available": "yes",
        "repair_history_count": 2,
        "repair_report_available": "no",
    }
    res = check_missing_documents(claim=claim)
    assert res["is_complete"] is False
    assert "repair_report" in res["missing_mandatory_docs"]
    assert res["repair_report_required"] is True


def test_missing_all_count_tracks_every_flag():
    """`missing_all_count` covers all six tracked document flags."""
    claim = {
        "product_category": "electronics",
        "receipt_available": "yes",
        "serial_evidence_available": "yes",
        "fault_evidence_available": "yes",
    }
    res = check_missing_documents(claim)
    assert res["is_complete"] is True
    assert res["missing_count"] == 0
    assert res["missing_all_count"] == 3  # warranty_card, product_image, repair_report
