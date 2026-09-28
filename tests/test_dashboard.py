"""
Unit and API Integration tests for User Dashboard and Admin Dashboard Statistics.
"""

import pytest


def test_user_dashboard(client, customer_headers, sample_warranty):
    """Test customer personal dashboard statistics via /dashboard/user and /dashboard/customer."""
    client.post(
        "/api/v1/claims/",
        json={
            "warranty_id": sample_warranty.id,
            "fault_type": "Trackpad Failure",
            "description": "Multi-touch trackpad unresponsive to gesture input.",
            "claim_amount": 80.0,
        },
        headers=customer_headers,
    )

    response = client.get("/api/v1/dashboard/user", headers=customer_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_warranties" in data
    assert data["total_warranties"] >= 1
    assert "active_warranties" in data
    assert "total_claims" in data
    assert data["total_claims"] >= 1
    assert "claims_by_status" in data

    cust_res = client.get("/api/v1/dashboard/customer", headers=customer_headers)
    assert cust_res.status_code == 200
    assert cust_res.json()["total_warranties"] == data["total_warranties"]


def test_user_dashboard_unauthorized(client):
    """Test accessing user dashboard without auth fails."""
    response = client.get("/api/v1/dashboard/user")
    assert response.status_code in [401, 403]


def test_admin_dashboard(client, admin_headers, sample_warranty):
    """Test admin consolidated metrics and operational telemetry."""
    response = client.get("/api/v1/dashboard/admin", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_claims" in data
    assert "approval_rate" in data
    assert "rejection_rate" in data
    assert "manual_review_rate" in data
    assert "average_turnaround_hours" in data
    assert "claims_by_status" in data
    assert "claims_by_category" in data


def test_admin_dashboard_forbidden_customer(client, customer_headers):
    """Test customer role forbidden from admin dashboard."""
    response = client.get("/api/v1/dashboard/admin", headers=customer_headers)
    assert response.status_code == 403