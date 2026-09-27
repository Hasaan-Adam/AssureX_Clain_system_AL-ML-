"""
Unit and API Integration tests for Product Catalog Management.
"""

import pytest


def test_list_products_empty(client):
    """Test listing products when catalog is empty."""
    response = client.get("/api/v1/products/")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "products" in data


def test_create_product_admin(client, admin_headers):
    """Test creating product by admin/staff user."""
    payload = {
        "model_name": "ThinkPad X1 Carbon",
        "category": "ELECTRONICS",
        "brand": "Lenovo",
        "serial_prefix": "LNV-X1-",
        "msrp": 1899.99,
        "warranty_months": 36,
        "description": "Ultra-light business laptop",
        "is_active": True,
    }
    response = client.post("/api/v1/products/", json=payload, headers=admin_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["model_name"] == "ThinkPad X1 Carbon"
    assert data["brand"] == "Lenovo"
    assert data["warranty_months"] == 36
    assert "id" in data


def test_create_product_forbidden_for_customer(client, customer_headers):
    """Customer role cannot create product catalog entries."""
    payload = {
        "model_name": "Forbidden Device",
        "category": "ELECTRONICS",
        "brand": "Unknown",
        "msrp": 500.0,
        "warranty_months": 12,
    }
    response = client.post("/api/v1/products/", json=payload, headers=customer_headers)
    assert response.status_code == 403


def test_get_product_by_id(client, sample_product):
    """Test retrieving product by ID."""
    response = client.get(f"/api/v1/products/{sample_product.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_product.id
    assert data["model_name"] == sample_product.model_name


def test_get_categories_and_brands(client, sample_product):
    """Test retrieving distinct product categories and brands."""
    cat_res = client.get("/api/v1/products/categories")
    assert cat_res.status_code == 200
    cats = cat_res.json()
    assert isinstance(cats, list)
    assert sample_product.category in cats

    brand_res = client.get("/api/v1/products/brands")
    assert brand_res.status_code == 200
    brands = brand_res.json()
    assert isinstance(brands, list)
    assert sample_product.brand in brands


def test_update_product(client, admin_headers, sample_product):
    """Test updating existing product catalog item."""
    update_payload = {
        "msrp": 1399.00,
        "warranty_months": 36,
    }
    response = client.put(f"/api/v1/products/{sample_product.id}", json=update_payload, headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["msrp"] == 1399.00
    assert data["warranty_months"] == 36