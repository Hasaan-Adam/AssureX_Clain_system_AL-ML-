"""
Unit tests for Claim Preparation Assistance and Hidden Readiness Scoring.
"""

import pytest
from src.services.prep_assist_service import analyze_claim_readiness


def test_claim_readiness_complete():
    """Verify completely filled claim has high readiness score."""
    payload = {
        "warranty_id": 1,
        "serial_number": "ELC-DEL-984830",
        "fault_type": "Display Glitch",
        "description": "Flickering vertical green lines on upper screen.",
        "receipt_available": "yes",
        "serial_evidence_available": "yes",
        "fault_evidence_available": "yes",
    }
    res = analyze_claim_readiness(payload)
    assert res["is_ready"] is True
    assert res["readiness_score"] >= 75
    assert len(res["blockers"]) == 0


def test_claim_readiness_incomplete():
    """Verify missing description and warranty lowers readiness score."""
    payload = {
        "fault_type": "Display Glitch",
        "description": "",
    }
    res = analyze_claim_readiness(payload)
    assert res["is_ready"] is False
    assert res["readiness_score"] < 75
    assert len(res["missing_items"]) >= 1