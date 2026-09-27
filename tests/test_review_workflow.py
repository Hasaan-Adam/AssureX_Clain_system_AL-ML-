"""
Unit and API Integration tests for Reviewer Queue, Manual Decisions, and Human Override Analytics.
"""

import pytest
from src.utils.constants import DecisionType


def test_review_queue_and_decision(client, reviewer_headers, customer_headers, sample_warranty):
    """Test manual review queue fetch and submitting decision."""
    # Submit claim
    payload = {
        "warranty_id": sample_warranty.id,
        "fault_type": "Motherboard Failure",
        "description": "System does not POST after firmware update.",
        "claim_amount": 400.0,
    }
    res = client.post("/api/v1/claims/", json=payload, headers=customer_headers)
    assert res.status_code == 201
    claim_id = res.json()["id"]

    # Check review queue
    queue_res = client.get("/api/v1/reviews/queue", headers=reviewer_headers)
    assert queue_res.status_code == 200
    queue_data = queue_res.json()
    assert "total" in queue_data
    assert "items" in queue_data
    assert any(item["id"] == claim_id for item in queue_data["items"])

    # Submit review decision (APPROVE)
    dec_payload = {
        "decision": DecisionType.APPROVE.value,
        "reasoning": "Motherboard defect confirmed covered under manufacturer warranty.",
        "notes": "Fast-tracked repair part shipment.",
    }
    dec_res = client.post(f"/api/v1/reviews/{claim_id}/decision", json=dec_payload, headers=reviewer_headers)
    assert dec_res.status_code == 200
    dec_data = dec_res.json()
    assert dec_data["decision"] == DecisionType.APPROVE.value
    assert dec_data["claim_id"] == claim_id
    assert dec_data["new_status"] == "approved"


def test_review_decision_reject_and_escalate(client, reviewer_headers, customer_headers, sample_warranty):
    """Test REJECT and ESCALATE decision flows."""
    # Create claim 1 for reject
    p1 = {
        "warranty_id": sample_warranty.id,
        "fault_type": "Water Damage",
        "description": "Submerged in pool during vacation.",
        "claim_amount": 800.0,
    }
    c1_res = client.post("/api/v1/claims/", json=p1, headers=customer_headers)
    c1_id = c1_res.json()["id"]

    rej_res = client.post(
        f"/api/v1/reviews/{c1_id}/decision",
        json={"decision": "REJECT", "reasoning": "Liquid ingress is excluded under standard policy terms."},
        headers=reviewer_headers,
    )
    assert rej_res.status_code == 200
    assert rej_res.json()["decision"] == "REJECT"
    assert rej_res.json()["new_status"] == "rejected"

    # Create claim 2 for escalate
    p2 = {
        "warranty_id": sample_warranty.id,
        "fault_type": "Intermittent Power Loss",
        "description": "Device shuts down randomly under heavy load.",
        "claim_amount": 1200.0,
    }
    c2_res = client.post("/api/v1/claims/", json=p2, headers=customer_headers)
    c2_id = c2_res.json()["id"]

    esc_res = client.post(
        f"/api/v1/reviews/{c2_id}/decide",
        json={"decision": "ESCALATE", "justification": "Requires Level 3 engineering inspection."},
        headers=reviewer_headers,
    )
    assert esc_res.status_code == 200
    assert esc_res.json()["decision"] == "ESCALATE"
    assert esc_res.json()["new_status"] == "escalated"


def test_manual_override_and_statistics(client, reviewer_headers, customer_headers, sample_warranty):
    """Test manual AI override and verify statistics reflect the override."""
    payload = {
        "warranty_id": sample_warranty.id,
        "fault_type": "Screen Artifacts",
        "description": "Display flickers on cold boot.",
        "claim_amount": 250.0,
    }
    c_res = client.post("/api/v1/claims/", json=payload, headers=customer_headers)
    claim_id = c_res.json()["id"]

    # Override automated decision using the /override alias
    override_payload = {
        "decision": "APPROVE",
        "justification": "Goodwill exception approved per regional manager instructions.",
    }
    ov_res = client.post(f"/api/v1/reviews/{claim_id}/override", json=override_payload, headers=reviewer_headers)
    assert ov_res.status_code == 200
    assert ov_res.json()["decision"] == "APPROVE"

    # Verify statistics
    res = client.get("/api/v1/reviews/stats/overrides", headers=reviewer_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total_reviewed"] >= 1
    assert "override_rate" in data
    assert "agreement_rate" in data
    assert "reviewer_breakdown" in data


def test_review_queue_filters(client, reviewer_headers):
    """Test review queue filtering with status and fraud score params."""
    res = client.get("/api/v1/reviews/queue?status=under_review&min_fraud_score=0.0&skip=0&limit=10", headers=reviewer_headers)
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert "total" in data


def test_review_rbac_security(client, customer_headers):
    """Ensure customer users cannot access reviewer queue or submit adjudication decisions."""
    # Customer cannot fetch review queue
    q_res = client.get("/api/v1/reviews/queue", headers=customer_headers)
    assert q_res.status_code == 403

    # Customer cannot submit decision
    d_res = client.post("/api/v1/reviews/1/decision", json={"decision": "APPROVE", "reasoning": "Self approve"}, headers=customer_headers)
    assert d_res.status_code == 403


def test_review_decision_validation_errors(client, reviewer_headers):
    """Test 404 on missing claim and 400 on invalid decision."""
    # Non-existent claim
    res = client.post(
        "/api/v1/reviews/999999/decision",
        json={"decision": "APPROVE", "reasoning": "Non existent"},
        headers=reviewer_headers,
    )
    assert res.status_code == 404

    # Invalid decision type
    inv_res = client.post(
        "/api/v1/reviews/1/decision",
        json={"decision": "INVALID_DECISION_TYPE", "reasoning": "Invalid payload testing"},
        headers=reviewer_headers,
    )
    # Either 404 (if claim 1 doesn't exist) or 400 (validation error)
    assert inv_res.status_code in [400, 404]