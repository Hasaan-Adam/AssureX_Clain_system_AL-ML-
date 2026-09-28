"""
Unit and Integration tests for Analytics API endpoints.
Tests:
- GET /api/v1/analytics/overview
- GET /api/v1/analytics/trends
- GET /api/v1/analytics/faults
- GET /api/v1/analytics/reliability
- GET /api/v1/analytics/fraud
- Role-based access control and boundary validations
"""

import pytest


def test_analytics_overview(client, staff_headers, sample_warranty):
    """Test retrieving complete analytics overview with staff credentials."""
    client.post(
        "/api/v1/claims/",
        json={
            "warranty_id": sample_warranty.id,
            "fault_type": "Screen Flickering",
            "description": "OLED panel intermittent flickering under high brightness.",
            "claim_amount": 120.0,
        },
        headers=staff_headers,
    )

    response = client.get("/api/v1/analytics/overview", headers=staff_headers)
    assert response.status_code == 200
    data = response.json()

    assert "time_series" in data
    assert isinstance(data["time_series"], list)
    assert len(data["time_series"]) > 0
    assert "date" in data["time_series"][0]
    assert "total_claims" in data["time_series"][0]

    assert "fault_distribution" in data
    assert isinstance(data["fault_distribution"], list)

    assert "brand_reliability" in data
    assert isinstance(data["brand_reliability"], list)
    assert len(data["brand_reliability"]) > 0

    assert "fraud_stats" in data
    assert "average_fraud_score" in data["fraud_stats"]
    assert "top_fraud_indicators" in data["fraud_stats"]


def test_analytics_overview_unauthorized(client):
    """Test that unauthenticated requests to analytics overview fail with 401."""
    response = client.get("/api/v1/analytics/overview")
    assert response.status_code in [401, 403]


def test_analytics_overview_forbidden_customer(client, customer_headers):
    """Test that customers cannot access staff-only analytics overview (403)."""
    response = client.get("/api/v1/analytics/overview", headers=customer_headers)
    assert response.status_code == 403


def test_analytics_trends_default(client, staff_headers):
    """Test retrieving 30-day analytics trends."""
    response = client.get("/api/v1/analytics/trends", headers=staff_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 30
    for point in data:
        assert "date" in point
        assert "total_claims" in point
        assert "approved" in point
        assert "rejected" in point
        assert "under_review" in point


def test_analytics_trends_custom_days(client, staff_headers):
    """Test retrieving analytics trends with custom days parameter."""
    response = client.get("/api/v1/analytics/trends?days=14", headers=staff_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 14


def test_analytics_trends_invalid_days(client, staff_headers):
    """Test validation on trends days parameter (must be between 7 and 180)."""
    response = client.get("/api/v1/analytics/trends?days=3", headers=staff_headers)
    assert response.status_code == 422

    response = client.get("/api/v1/analytics/trends?days=365", headers=staff_headers)
    assert response.status_code == 422


def test_analytics_faults(client, staff_headers):
    """Test retrieving fault type distribution."""
    response = client.get("/api/v1/analytics/faults", headers=staff_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_analytics_reliability(client, staff_headers):
    """Test retrieving brand reliability ratings."""
    response = client.get("/api/v1/analytics/reliability", headers=staff_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        item = data[0]
        assert "brand" in item
        assert "total_warranties" in item
        assert "reliability_score" in item


def test_analytics_fraud_reviewer(client, reviewer_headers):
    """Test retrieving fraud detection stats with reviewer permissions."""
    response = client.get("/api/v1/analytics/fraud", headers=reviewer_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_flagged_claims" in data
    assert "average_fraud_score" in data
    assert "high_risk_claims_count" in data
    assert "top_fraud_indicators" in data
