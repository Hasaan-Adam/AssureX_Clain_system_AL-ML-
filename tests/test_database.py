"""
Unit and Integration tests for AssureX Database Connection, Models, and Seeding.

Field names follow the SRS data dictionary
(documentation/project_report/09_data_dictionary.md).
"""

from datetime import date, timedelta
import json
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.connection import Base
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
    """In-memory SQLite database session fixture."""
    test_engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=test_engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


def _make_user(email: str = "test_user@assurex.com", role: str = RoleEnum.CUSTOMER.value) -> User:
    return User(email=email, hashed_password="fake_hashed_pw", full_name="Test User", role=role)


def _make_product(
    user_id: int,
    serial: str = "SMG-24-0001",
    name: str = "Galaxy Ultra S24",
    category: str = ProductCategory.MOBILE_PHONES.value,
    brand: str = "Samsung",
    price: int = 1200,
) -> Product:
    today = date.today()
    return Product(
        product_id=f"PRD-{serial}",
        owner_id=user_id,
        name=name,
        category=category,
        brand=brand,
        model_number=brand[:3].upper() + "-1000",
        serial_number=serial,
        purchase_date=today - timedelta(days=10),
        purchase_price=price,
        retailer="AssureX Store",
        warranty_duration_months=12,
        warranty_start_date=today - timedelta(days=10),
        warranty_expiry_date=today + timedelta(days=355),
    )


def test_user_creation(test_db):
    user = _make_user()
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    assert user.id is not None
    assert user.email == "test_user@assurex.com"
    assert user.is_active is True


def test_product_creation(test_db):
    user = _make_user()
    test_db.add(user)
    test_db.commit()

    product = _make_product(user.id)
    test_db.add(product)
    test_db.commit()
    test_db.refresh(product)

    assert product.id is not None
    assert product.name == "Galaxy Ultra S24"
    assert product.product_id == "PRD-SMG-24-0001"
    assert product.owner_id == user.id


def test_product_id_is_generated_when_omitted(test_db):
    """The business key is derived, never left NULL."""
    user = _make_user("gen@assurex.com")
    test_db.add(user)
    test_db.commit()

    product = _make_product(user.id, serial="SNY-XR65-12345", name="Bravia XR 65", brand="Sony", category="ELECTRONICS")
    product.product_id = None
    test_db.add(product)
    test_db.commit()
    test_db.refresh(product)

    assert product.product_id.startswith("PRD-")
    assert product.product_id.endswith("12345")


def test_warranty_and_claim_relationship(test_db):
    user = _make_user("customer1@example.com")
    test_db.add(user)
    test_db.commit()

    product = _make_product(user.id, serial="SNY-XR65-12345", name="Bravia XR 65", brand="Sony", category="ELECTRONICS", price=1800)
    test_db.add(product)
    test_db.commit()

    today = date.today()
    warranty = Warranty(
        warranty_number="WRN-TEST-101",
        user_id=user.id,
        product_id=product.id,
        serial_number=product.serial_number,
        start_date=product.warranty_start_date,
        purchase_date=today - timedelta(days=30),
        expiry_date=today + timedelta(days=335),
        status=WarrantyStatus.ACTIVE.value,
        purchase_price=1800.0,
        warranty_duration_months=12,
    )
    test_db.add(warranty)
    test_db.commit()
    test_db.refresh(warranty)

    claim = Claim(
        claim_id="CLM-TEST-202",
        claimant_id=user.id,
        product_id=product.id,
        warranty_id=warranty.id,
        fault_occurrence_date=today - timedelta(days=5),
        fault_type="DISPLAY_DEFECT",
        fault_description="Dead pixel line across top edge",
        claim_amount=250.0,
        claim_submission_date=today,
        status=ClaimStatus.SUBMITTED.value,
        created_by=user.id,
        filing_channel="self_service",
    )
    test_db.add(claim)
    test_db.commit()
    test_db.refresh(claim)

    assert claim.id is not None
    assert claim.claimant_id == user.id
    assert claim.warranty.warranty_number == "WRN-TEST-101"
    assert len(warranty.claims) == 1
    assert warranty.claims[0].claim_id == "CLM-TEST-202"


def test_document_and_prediction(test_db):
    user = _make_user("u@x.com")
    test_db.add(user)
    test_db.commit()

    prod = _make_product(user.id, serial="ELC-DEL-984830", name="Power Supply 650W", brand="Dell", category="ELECTRONICS", price=100)
    test_db.add(prod)
    test_db.commit()

    warranty = Warranty(
        warranty_number="WRN-T1",
        user_id=user.id,
        product_id=prod.id,
        serial_number=prod.serial_number,
        start_date=prod.warranty_start_date,
        purchase_date=prod.purchase_date,
        expiry_date=date.today() + timedelta(days=365),
    )
    test_db.add(warranty)
    test_db.commit()

    claim = Claim(
        claim_id="CLM-T1",
        claimant_id=user.id,
        product_id=prod.id,
        warranty_id=warranty.id,
        fault_occurrence_date=date.today(),
        fault_type="POWER_FAILURE",
        fault_description="No boot",
        status=ClaimStatus.SUBMITTED.value,
    )
    test_db.add(claim)
    test_db.commit()

    doc = Document(
        claim_id=claim.id,
        uploader_id=user.id,
        document_type="purchase_receipt",
        file_path="/tmp/inv.pdf",
        file_size=1024,
        mime_type="application/pdf",
        file_hash="f" * 64,
    )
    pred = Prediction(
        claim_id=claim.id,
        python_predicted_class=DecisionType.APPROVE.value,
        python_probabilities=json.dumps({"Valid Claim": 0.91, "Invalid Claim": 0.06, "Manual Review": 0.03}),
        tm_predicted_class=DecisionType.APPROVE.value,
        tm_probabilities=json.dumps({"Valid Claim": 0.88, "Invalid Claim": 0.08, "Manual Review": 0.04}),
        comparison_result="models_agree",
        final_decision=DecisionType.APPROVE.value,
    )
    test_db.add_all([doc, pred])
    test_db.commit()

    assert len(claim.documents) == 1
    assert len(claim.predictions) == 1
    assert claim.documents[0].file_name == "inv.pdf"
    assert claim.predictions[0].confidence_score == 0.91
    assert claim.predictions[0].python_predicted_class == "APPROVE"


def test_admin_settings_crud(test_db):
    setting = AdminSetting(
        key="test_feature_flag",
        value={"enabled": True, "limit": 50},
        description="Feature flag for testing",
    )
    test_db.add(setting)
    test_db.commit()
    test_db.refresh(setting)

    assert setting.id is not None
    assert setting.value["enabled"] is True
