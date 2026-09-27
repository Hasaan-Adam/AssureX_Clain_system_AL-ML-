"""
Unit and API Integration tests for PDF Claim Report Generation and CSV/Excel Dataset Exports.
"""

import pytest


def test_claim_pdf_report_download(client, customer_headers, sample_warranty):
    """Test generating and downloading PDF claim adjudication report."""
    # Submit claim
    create_res = client.post(
        "/api/v1/claims/",
        json={
            "warranty_id": sample_warranty.id,
            "fault_type": "Battery Failure",
            "description": "Battery completely non-functional.",
            "claim_amount": 100.0,
        },
        headers=customer_headers,
    )
    claim_id = create_res.json()["id"]

    response = client.get(f"/api/v1/reports/claim/{claim_id}/pdf", headers=customer_headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert len(response.content) > 100
    assert response.content.startswith(b"%PDF")


def test_export_claims_csv(client, admin_headers, sample_warranty):
    """Test exporting claims records as CSV."""
    response = client.get("/api/v1/reports/export/claims/csv", headers=admin_headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "Claim Number" in response.text


def test_export_claims_excel(client, admin_headers, sample_warranty):
    """Test exporting claims records as Excel .xlsx workbook."""
    response = client.get("/api/v1/reports/export/claims/excel", headers=admin_headers)
    assert response.status_code == 200
    assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in response.headers["content-type"]
    assert len(response.content) > 100


def test_export_reviews_csv(client, admin_headers):
    """Test exporting reviewer audit logs as CSV."""
    response = client.get("/api/v1/reports/export/reviews/csv", headers=admin_headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "Review ID" in response.text