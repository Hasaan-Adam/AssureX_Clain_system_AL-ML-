"""
Pytest configuration and shared fixtures for AssureX Claim Engine tests.
"""

from datetime import date, datetime, timedelta, timezone
import os
from pathlib import Path
import sys
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from database.connection import Base
from database.session import get_db
from src.core.security import create_access_token, hash_password
from src.main import app
from src.models import (
    AdminSetting,
    AuditLog,
    Claim,
    Document,
    Notification,
    Prediction,
    Product,
    Repair,
    Review,
    User,
    Warranty,
)
from src.utils.constants import ClaimStatus, DecisionType, ProductCategory, RoleEnum, WarrantyStatus


@pytest.fixture(scope="function")
def test_db():
    """Shared in-memory SQLite database session fixture with StaticPool."""
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=test_engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(test_db):
    """FastAPI TestClient with overridden database dependency."""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def customer_user(test_db):
    """Fixture creating a standard active customer user."""
    user = User(
        email="customer@assurex.com",
        hashed_password=hash_password("Password123!"),
        full_name="John Customer",
        role=RoleEnum.CUSTOMER.value,
        is_active=True,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def reviewer_user(test_db):
    """Fixture creating a reviewer user."""
    user = User(
        email="reviewer@assurex.com",
        hashed_password=hash_password("Password123!"),
        full_name="Jane Reviewer",
        role=RoleEnum.REVIEWER.value,
        is_active=True,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def admin_user(test_db):
    """Fixture creating an admin user."""
    user = User(
        email="admin@assurex.com",
        hashed_password=hash_password("Password123!"),
        full_name="Super Admin",
        role=RoleEnum.ADMIN.value,
        is_active=True,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def staff_user(test_db):
    """Fixture creating a staff user."""
    user = User(
        email="staff@assurex.com",
        hashed_password=hash_password("Password123!"),
        full_name="Steve Staff",
        role=RoleEnum.STAFF.value,
        is_active=True,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def customer_token(customer_user):
    """Access token for customer user."""
    return create_access_token(subject=customer_user.id, role=customer_user.role)


@pytest.fixture
def customer_headers(customer_token):
    """HTTP headers with customer token."""
    return {"Authorization": f"Bearer {customer_token}"}


@pytest.fixture
def reviewer_token(reviewer_user):
    """Access token for reviewer user."""
    return create_access_token(subject=reviewer_user.id, role=reviewer_user.role)


@pytest.fixture
def reviewer_headers(reviewer_token):
    """HTTP headers with reviewer token."""
    return {"Authorization": f"Bearer {reviewer_token}"}


@pytest.fixture
def admin_token(admin_user):
    """Access token for admin user."""
    return create_access_token(subject=admin_user.id, role=admin_user.role)


@pytest.fixture
def admin_headers(admin_token):
    """HTTP headers with admin token."""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def staff_token(staff_user):
    """Access token for staff user."""
    return create_access_token(subject=staff_user.id, role=staff_user.role)


@pytest.fixture
def staff_headers(staff_token):
    """HTTP headers with staff token."""
    return {"Authorization": f"Bearer {staff_token}"}


@pytest.fixture
def sample_product(test_db, customer_user):
    """Fixture creating a sample product in catalog."""
    today = date.today()
    product = Product(
        product_id="PRD-TEST-00001",
        owner_id=customer_user.id,
        name="XPS 15",
        category=ProductCategory.ELECTRONICS.value,
        brand="Dell",
        model_number="XPS-9520",
        serial_number="ELC-DEL-984830",
        purchase_date=today - timedelta(days=60),
        purchase_price=1500,
        warranty_duration_months=24,
        warranty_type="standard",
        warranty_start_date=today - timedelta(days=60),
        warranty_expiry_date=today + timedelta(days=670),
    )
    test_db.add(product)
    test_db.commit()
    test_db.refresh(product)
    return product


@pytest.fixture
def sample_warranty(test_db, customer_user, sample_product):
    """Fixture creating a sample warranty."""
    today = date.today()
    warranty = Warranty(
        warranty_number="WRN-TEST-00001",
        user_id=customer_user.id,
        product_id=sample_product.id,
        serial_number=sample_product.serial_number,
        provider="City Mart Stores",
        start_date=today - timedelta(days=60),
        purchase_date=today - timedelta(days=60),
        expiry_date=today + timedelta(days=670),
        status="ACTIVE",
        purchase_price=float(sample_product.purchase_price),
        coverage_conditions="Standard manufacturer hardware coverage",
    )
    test_db.add(warranty)
    test_db.commit()
    test_db.refresh(warranty)
    return warranty


@pytest.fixture
def sample_valid_claim_dict():
    """Provides a sample valid claim dictionary."""
    return {
        "claim_id": "CLM-VALID-001",
        "product_name": "Laptop",
        "product_category": "electronics",
        "brand": "Dell",
        "model_number": "DE926-ELE",
        "serial_number": "ELC-DEL-984830",
        "serial_status": "match",
        "purchase_date": "2024-05-13",
        "purchase_price": 308176,
        "retailer": "City Mart Stores",
        "warranty_duration_months": 36,
        "warranty_type": "standard",
        "warranty_start_date": "2024-05-13",
        "warranty_expiry_date": "2027-05-13",
        "claim_submission_date": "2024-10-15",
        "product_age_days": 155,
        "remaining_warranty_days": 940,
        "fault_occurrence_date": "2024-10-10",
        "fault_type": "battery_degradation",
        "fault_description": "Intermittent fault observed",
        "damage_type": "manufacturing_defect",
        "covered_fault": "yes",
        "claim_reporting_days": 5,
        "within_reporting_period": "yes",
        "reporting_deadline_days": 30,
        "repair_history_count": 0,
        "repair_authorized": "none",
        "previous_replacement": "no",
        "receipt_available": "yes",
        "warranty_card_available": "yes",
        "product_image_available": "yes",
        "serial_evidence_available": "yes",
        "fault_evidence_available": "yes",
        "repair_report_available": "yes",
        "missing_document_count": 0,
        "mandatory_docs_complete": "yes",
        "has_contradiction": "no",
        "contradiction_type": "none",
        "is_duplicate": "no",
        "proof_of_purchase": "yes",
        "warranty_active": "yes",
        "excluded_damage": "no",
        "ocr_quality": "high",
    }