"""
Unit and API Integration tests for Claim Submission, Pipeline Adjudication, Status Transitions, and Appeals.
"""

from datetime import date
import pytest
from src.utils.constants import ClaimStatus


def test_submit_claim_success(client, customer_headers, sample_warranty):
    """Test customer submitting a new warranty claim."""
    payload = {
        "warranty_id": sample_warranty.id,
        "fault_type": "Display Defect",
        "description": "Flickering vertical line across lower LCD panel.",
        "claim_amount": 250.0,
    }
    response = client.post("/api/v1/claims/", json=payload, headers=customer_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["warranty_id"] == sample_warranty.id
    assert data["fault_type"] == "Display Defect"
    assert "claim_number" in data
    assert data["claim_number"].startswith("CLM-")
    assert data["status"] in ["submitted", "auto_approved", "approved", "under_review", "rejected"]


def test_submit_claim_invalid_warranty(client, customer_headers):
    """Attempting claim on non-existent warranty returns 404."""
    payload = {
        "warranty_id": 999999,
        "fault_type": "Battery Issue",
        "description": "Battery completely dead.",
        "claim_amount": 100.0,
    }
    response = client.post("/api/v1/claims/", json=payload, headers=customer_headers)
    assert response.status_code == 404


def test_claim_status_transitions(client, reviewer_headers, customer_headers, sample_warranty):
    """Test claim status lifecycle transition by reviewer."""
    # Submit claim
    payload = {
        "warranty_id": sample_warranty.id,
        "fault_type": "Speaker Buzzing",
        "description": "Static buzz on left speaker channel.",
        "claim_amount": 75.0,
    }
    create_res = client.post("/api/v1/claims/", json=payload, headers=customer_headers)
    claim_id = create_res.json()["id"]

    # Transition to under_review
    trans_payload = {
        "status": "under_review",
        "notes": "Assigned for manual technician inspection.",
    }
    trans_res = client.put(f"/api/v1/claims/{claim_id}/status", json=trans_payload, headers=reviewer_headers)
    assert trans_res.status_code == 200
    assert trans_res.json()["status"] == "under_review"

    # Transition to approved
    app_payload = {"status": "approved", "reason": "Defect confirmed under warranty."}
    app_res = client.put(f"/api/v1/claims/{claim_id}/status", json=app_payload, headers=reviewer_headers)
    assert app_res.status_code == 200
    assert app_res.json()["status"] == "approved"
    assert app_res.json()["final_decision"] == "APPROVE"


def test_claim_appeal_workflow(client, reviewer_headers, customer_headers, sample_warranty):
    """Test customer appealing a rejected claim."""
    # Submit claim
    payload = {
        "warranty_id": sample_warranty.id,
        "fault_type": "Power Glitch",
        "description": "Random power down on AC disconnect.",
        "claim_amount": 120.0,
    }
    create_res = client.post("/api/v1/claims/", json=payload, headers=customer_headers)
    claim_id = create_res.json()["id"]

    # Reject claim
    client.put(
        f"/api/v1/claims/{claim_id}/status",
        json={"status": "rejected", "reason": "Insufficient diagnostics"},
        headers=reviewer_headers,
    )

    # Customer submits appeal
    appeal_payload = {
        "appeal_notes": "Attached certified diagnostics report from authorized repair center.",
    }
    appeal_res = client.post(f"/api/v1/claims/{claim_id}/appeal", json=appeal_payload, headers=customer_headers)
    assert appeal_res.status_code == 200
    data = appeal_res.json()
    assert data["status"] == "appeal_requested"
    assert data["appeal_notes"] == appeal_payload["appeal_notes"]