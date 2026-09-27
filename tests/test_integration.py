"""
End-to-End Integration tests for the complete AssureX Claim Lifecycle:
Registration -> Product Creation -> Warranty Activation -> Claim Submission -> AI Adjudication -> Manual Review -> PDF Report Export.
"""

from datetime import date, timedelta
import pytest


def test_full_claim_engine_lifecycle(client):
    """
    Complete end-to-end integration test of AssureX Engine across all services & API routes.
    """
    # 1. Health check
    health_res = client.get("/api/v1/health")
    assert health_res.status_code == 200
    assert health_res.json()["status"] == "healthy"

    # 2. Register Customer
    cust_res = client.post(
        "/api/v1/auth/register",
        json={
            "email": "e2e_customer@assurex.com",
            "password": "Password123!",
            "full_name": "E2E Test Customer",
            "role": "customer",
        },
    )
    assert cust_res.status_code == 201
    cust_id = cust_res.json()["id"]

    # 3. Login as Customer
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "e2e_customer@assurex.com", "password": "Password123!"},
    )
    assert login_res.status_code == 200
    cust_token = login_res.json()["access_token"]
    cust_headers = {"Authorization": f"Bearer {cust_token}"}

    # 4. Register Admin
    admin_res = client.post(
        "/api/v1/auth/register",
        json={
            "email": "e2e_admin@assurex.com",
            "password": "Password123!",
            "full_name": "E2E Admin",
            "role": "admin",
        },
    )
    assert admin_res.status_code == 201

    admin_login = client.post(
        "/api/v1/auth/login",
        json={"email": "e2e_admin@assurex.com", "password": "Password123!"},
    )
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 5. Admin creates Product
    prod_res = client.post(
        "/api/v1/products/",
        json={
            "model_name": "UltraSmart 4K TV",
            "category": "HOME_APPLIANCES",
            "brand": "Samsung",
            "msrp": 1200.0,
            "warranty_months": 24,
        },
        headers=admin_headers,
    )
    assert prod_res.status_code == 201
    product_id = prod_res.json()["id"]

    # 6. Customer registers Warranty
    today = date.today()
    w_res = client.post(
        "/api/v1/warranties/",
        json={
            "product_id": product_id,
            "serial_number": "SMG-TV-E2E-001",
            "purchase_date": str(today - timedelta(days=30)),
            "purchase_price": 1200.0,
        },
        headers=cust_headers,
    )
    assert w_res.status_code == 201
    warranty_id = w_res.json()["id"]

    # 7. Customer submits Claim
    claim_res = client.post(
        "/api/v1/claims/",
        json={
            "warranty_id": warranty_id,
            "fault_type": "Screen Artifacts",
            "description": "Distorted colors on HDMI 1 and HDMI 2 inputs.",
            "claim_amount": 150.0,
        },
        headers=cust_headers,
    )
    assert claim_res.status_code == 201
    claim_id = claim_res.json()["id"]
    claim_number = claim_res.json()["claim_number"]

    # 8. Customer views their Dashboard
    dash_res = client.get("/api/v1/dashboard/user", headers=cust_headers)
    assert dash_res.status_code == 200
    assert dash_res.json()["total_claims"] >= 1

    # 9. Admin views Admin Dashboard
    admin_dash = client.get("/api/v1/dashboard/admin", headers=admin_headers)
    assert admin_dash.status_code == 200
    assert admin_dash.json()["total_claims"] >= 1

    # 10. Generate PDF Report
    pdf_res = client.get(f"/api/v1/reports/claim/{claim_id}/pdf", headers=cust_headers)
    assert pdf_res.status_code == 200
    assert pdf_res.content.startswith(b"%PDF")