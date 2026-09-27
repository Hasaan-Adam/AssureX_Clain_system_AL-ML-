"""
Unit and API Integration tests for Warranty Registration, Expiration Calculation, and Alert Generation.
"""

from datetime import date, timedelta
import pytest
from src.services.warranty_service import generate_expiry_alerts


def test_register_warranty(client, customer_headers, customer_user, sample_product):
    """Test customer registering a product warranty."""
    today = date.today()
    payload = {
        "product_id": sample_product.id,
        "serial_number": "ELC-DEL-559922",
        "purchase_date": str(today - timedelta(days=10)),
        "purchase_price": 1450.00,
        "store_name": "Best Buy Downtown",
        "invoice_number": "INV-2024-9988",
    }
    response = client.post("/api/v1/warranties/", json=payload, headers=customer_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["serial_number"] == "ELC-DEL-559922"
    assert data["status"] == "ACTIVE"
    assert data["user_id"] == customer_user.id
    assert "warranty_number" in data
    assert data["warranty_number"].startswith("WRN-")


def test_duplicate_serial_warranty_conflict(client, customer_headers, sample_warranty, sample_product):
    """Attempting to register active warranty with same serial results in 409 conflict."""
    payload = {
        "product_id": sample_product.id,
        "serial_number": sample_warranty.serial_number,
        "purchase_date": str(date.today()),
        "purchase_price": 1500.0,
    }
    response = client.post("/api/v1/warranties/", json=payload, headers=customer_headers)
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CONFLICT"


def test_list_warranties(client, customer_headers, sample_warranty):
    """Test listing warranties for customer."""
    response = client.get("/api/v1/warranties/", headers=customer_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert any(w["id"] == sample_warranty.id for w in data["warranties"])


def test_verify_serial_endpoint(client, sample_warranty):
    """Test public serial warranty verification endpoint."""
    response = client.get(f"/api/v1/warranties/verify/{sample_warranty.serial_number}")
    assert response.status_code == 200
    data = response.json()
    assert data["exists"] is True
    assert data["warranty_number"] == sample_warranty.warranty_number
    assert data["status"] == "ACTIVE"


def test_warranty_expiry_alerts(client, test_db, admin_headers, customer_user, sample_product):
    """Test expiry alert notification generator."""
    today = date.today()
    # Create warranty expiring in 7 days (matches alert_days: [30, 15, 7, 0])
    w = sample_product
    from src.models.warranty import Warranty
    expiring_warranty = Warranty(
        warranty_number="WRN-ALERT-007",
        user_id=customer_user.id,
        product_id=sample_product.id,
        serial_number="ELC-DEL-ALERT7",
        start_date=today - timedelta(days=358),
        purchase_date=today - timedelta(days=358),
        expiry_date=today + timedelta(days=7),
        status="ACTIVE",
        purchase_price=1200.0,
    )
    test_db.add(expiring_warranty)
    test_db.commit()

    # Trigger alert check
    result = generate_expiry_alerts(test_db)
    assert result["alerts_generated"] >= 1
    assert any(d["warranty_number"] == "WRN-ALERT-007" for d in result["details"])