"""
Unit and API Integration tests for Claim Status Tracking & History Timeline.
"""

from datetime import date, timedelta

from src.services.claim_service import transition_claim_status


def test_status_tracking_timeline(test_db, sample_warranty, customer_user, reviewer_user):
    """Test full status tracking timeline and state updates."""
    from database.models import Claim
    claim = Claim(
        claim_id="CLM-TIMELINE-01",
        claimant_id=customer_user.id,
        product_id=sample_warranty.product_id,
        warranty_id=sample_warranty.id,
        fault_occurrence_date=date.today() - timedelta(days=5),
        fault_type="Audio Malfunction",
        fault_description="Headphone jack output non-functional.",
        damage_type="component_failure",
        claim_amount=60.0,
        claim_submission_date=date.today(),
        status="submitted",
    )
    test_db.add(claim)
    test_db.commit()

    # Step 1: AI adjudication in progress
    c1 = transition_claim_status(test_db, claim.id, "under_review", user_id=reviewer_user.id)
    assert c1.status == "under_review"
    assert c1.final_decision == "MANUAL_REVIEW"

    # Step 2: Rejected by reviewer
    c2 = transition_claim_status(
        test_db, claim.id, "rejected", user_id=reviewer_user.id, reason="Out of warranty period."
    )
    assert c2.status == "rejected"
    assert c2.final_decision == "REJECT"
    assert c2.rejection_reason == "Out of warranty period."

    # Step 3: Re-assigned and approved
    c3 = transition_claim_status(test_db, claim.id, "under_review", user_id=reviewer_user.id)
    assert c3.status == "under_review"
    c4 = transition_claim_status(
        test_db, claim.id, "approved", user_id=reviewer_user.id, reason="Validated defect."
    )
    assert c4.status == "approved"
    assert c4.final_decision == "APPROVE"
    assert c4.resolved_at is not None


def test_claim_timeline_endpoint_reports_real_events(
    client, customer_headers, sample_warranty
):
    """SRS xxxviii: the timeline endpoint returns recorded events, not guesses."""
    create_res = client.post(
        "/api/v1/claims/",
        json={
            "warranty_id": sample_warranty.id,
            "fault_type": "Screen Flicker",
            "description": "Intermittent vertical banding.",
            "claim_amount": 90.0,
        },
        headers=customer_headers,
    )
    assert create_res.status_code == 201
    claim_id = create_res.json()["id"]

    timeline = client.get(f"/api/v1/claims/{claim_id}/timeline", headers=customer_headers)
    assert timeline.status_code == 200
    body = timeline.json()
    assert body["claim_number"].startswith("CLM-")
    assert body["current_status"]
    stages = [s["stage"] for s in body["stages"]]
    assert {"draft", "submitted", "under_review", "approved", "rejected", "closed"}.issubset(set(stages))
    assert any(e["stage"] == "submitted" for e in body["events"])


def test_claim_audit_logs_endpoint(client, customer_headers, sample_warranty):
    """SRS xlvii: claim-level audit trail is exposed and owner-scoped."""
    create_res = client.post(
        "/api/v1/claims/",
        json={
            "warranty_id": sample_warranty.id,
            "fault_type": "Port Failure",
            "description": "USB-C port no longer charges.",
            "claim_amount": 45.0,
        },
        headers=customer_headers,
    )
    assert create_res.status_code == 201
    claim_id = create_res.json()["id"]

    logs_res = client.get(f"/api/v1/claims/{claim_id}/audit-logs", headers=customer_headers)
    assert logs_res.status_code == 200
    body = logs_res.json()
    assert body["total"] >= 1
    assert any(entry["action"] == "CLAIM_SUBMIT" for entry in body["logs"])


def test_claim_number_lookup_and_filters(client, customer_headers, sample_warranty):
    """SRS xlii: claims are retrievable by number and filterable."""
    create_res = client.post(
        "/api/v1/claims/",
        json={
            "warranty_id": sample_warranty.id,
            "fault_type": "Battery Swelling",
            "description": "Rear casing deformed.",
            "claim_amount": 150.0,
        },
        headers=customer_headers,
    )
    claim_number = create_res.json()["claim_number"]

    by_number = client.get(f"/api/v1/claims/by-number/{claim_number}", headers=customer_headers)
    assert by_number.status_code == 200
    assert by_number.json()["claim_number"] == claim_number

    filtered = client.get(
        "/api/v1/claims/?fault_type=Battery&search=Swelling",
        headers=customer_headers,
    )
    assert filtered.status_code == 200
    assert filtered.json()["total"] >= 1
