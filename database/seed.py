"""Database Seed Script - Initialize admin user, sample data, and policies"""

from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy.orm import Session

from database.connection import SessionLocal, engine, Base
from database.models import (
    User, Product, Warranty, Claim, Document, RepairHistory,
    AuditLog, Notification, ModelVersion,
    UserRole, ClaimStatus, WarrantyType, DocumentType,
)
from src.core.security import get_password_hash


def create_admin_user(db: Session) -> None:
    """Create default admin user if not exists."""
    from src.core.security import get_password_hash
    
    admin = db.query(User).filter(User.email == "admin@assurex.com").first()
    if not admin:
        admin = User(
            email="admin@assurex.com",
            hashed_password=get_password_hash("admin123"),
            full_name="System Administrator",
            phone="+92-300-1234567",
            role="admin",
            is_active=True,
        )
        db.add(admin)
        db.commit()
        print("[OK] Created admin user: admin@assurex.com / admin123")
    else:
        print("[OK] Admin user already exists")


def create_demo_users(db: Session) -> None:
    """Create demo users for each role."""
    from src.core.security import get_password_hash
    
    demo_users = [
        {"email": "customer@assurex.com", "password": "customer123", "full_name": "Demo Customer", "role": "customer"},
        {"email": "staff@assurex.com", "password": "staff123", "full_name": "Demo Service Staff", "role": "service_staff"},
        {"email": "reviewer@assurex.com", "password": "reviewer123", "full_name": "Demo Reviewer", "role": "reviewer"},
    ]
    
    for u in demo_users:
        existing = db.query(User).filter(User.email == u["email"]).first()
        if not existing:
            user = User(
                email=u["email"],
                hashed_password=get_password_hash(u["password"]),
                full_name=u["full_name"],
                role=u["role"],
                is_active=True,
            )
            db.add(user)
            print(f"[OK] Created demo user: {u['email']}")
    db.commit()


def create_policies(db: Session) -> None:
    """Policy files are JSON-based (in policies/ folder). No DB table needed."""
    # Policies are stored as JSON files in policies/ directory
    pass


def create_model_version_entry(db: Session) -> None:
    """Register initial model version."""
    existing = db.query(ModelVersion).filter(ModelVersion.version == "v1.0.0").first()
    if not existing:
        mv = ModelVersion(
            version="v1.0.0",
            algorithm="XGBClassifier",
            framework="xgboost",
            hyperparameters=json.dumps({
                "n_estimators": 150,
                "max_depth": 6,
                "learning_rate": 0.08,
                "subsample": 0.9,
                "colsample_bytree": 0.9,
            }),
            metrics=json.dumps({
                "val_accuracy": 1.0,
                "val_f1_macro": 1.0,
                "test_accuracy": 1.0,
                "test_f1_macro": 1.0,
            }),
            artifacts=json.dumps({
                "model_path": "model/python/claim_classifier.joblib",
                "preprocessor_path": "model/python/preprocessor.joblib",
                "label_encoder_path": "model/python/label_encoder.joblib",
                "feature_columns_path": "model/python/feature_columns.json",
            }),
            description="Initial XGBoost model trained on 1500 synthetic warranty claims",
            status="active",
        )
        db.add(mv)
        db.commit()
        print("[OK] Registered model version v1.0.0")


def create_sample_products(db: Session) -> None:
    """Create sample product catalog if not already populated."""
    from datetime import date, timedelta
    
    admin = db.query(User).filter(User.email == "admin@assurex.com").first()
    admin_id = admin.id if admin else 1
    
    products_data = [
        {"name": 'Samsung 65" 4K Neo QLED TV', "category": "electronics", "brand": "Samsung", "model": "QN65QN90C", "prefix": "ELC-SAM", "msrp": 218000, "months": 24},
        {"name": "iPhone 15 Pro Max 256GB", "category": "mobile_phones", "brand": "Apple", "model": "A3106", "prefix": "MPH-APP", "msrp": 465000, "months": 12},
        {"name": "Dell XPS 15 9530 Core i7", "category": "electronics", "brand": "Dell", "model": "XPS-9530-OLED", "prefix": "ELC-DEL", "msrp": 345000, "months": 12},
        {"name": "Panasonic Inverter Microwave 32L", "category": "home_appliances", "brand": "Panasonic", "model": "NN-ST65JB", "prefix": "HAP-PAN", "msrp": 42000, "months": 12},
        {"name": "Haier Inverter Refrigerator 438L", "category": "home_appliances", "brand": "Haier", "model": "HRF-438IDRA", "prefix": "HAP-HAI", "msrp": 148000, "months": 36},
        {"name": "Samsung Front Load EcoBubble Washer 9kg", "category": "home_appliances", "brand": "Samsung", "model": "WW90T554DAX", "prefix": "HAP-SAM", "msrp": 195000, "months": 24},
        {"name": 'Sony Bravia XR 55" OLED TV', "category": "electronics", "brand": "Sony", "model": "XR-55A80L", "prefix": "ELC-SON", "msrp": 380000, "months": 24},
        {"name": "HP Omen 16 Gaming Laptop", "category": "electronics", "brand": "HP", "model": "16-wf0033dx", "prefix": "ELC-HP", "msrp": 410000, "months": 12},
        {"name": "Gree Inverter Split AC 1.5 Ton", "category": "home_appliances", "brand": "Gree", "model": "GS-18FITH", "prefix": "HAP-GRE", "msrp": 165000, "months": 36},
        {"name": "Samsung Galaxy Watch 6 Classic", "category": "mobile_phones", "brand": "Samsung", "model": "SM-R960", "prefix": "MPH-SAM", "msrp": 72000, "months": 12},
        {"name": 'Apple iPad Air M2 11" 128GB', "category": "mobile_phones", "brand": "Apple", "model": "A2902", "prefix": "MPH-APP", "msrp": 175000, "months": 12},
    ]

    for idx, p in enumerate(products_data, 1):
        existing = db.query(Product).filter(Product.model_number == p["model"]).first()
        if not existing:
            prod = Product(
                product_id=f"PRD-{idx:04d}",
                owner_id=admin_id,
                name=p["name"],
                category=p["category"],
                brand=p["brand"],
                model_number=p["model"],
                serial_number=f"{p['prefix']}-{idx:06d}",
                purchase_date=date.today() - timedelta(days=60),
                purchase_price=p["msrp"],
                retailer="Official Flagship Outlet",
                warranty_duration_months=p["months"],
                warranty_type="standard",
                warranty_start_date=date.today() - timedelta(days=60),
                warranty_expiry_date=date.today() + timedelta(days=p["months"] * 30),
            )
            db.add(prod)
    db.commit()
    print(f"[OK] Seeded {len(products_data)} catalog products")


def create_sample_warranties_for_demo_customer(db: Session) -> None:
    """Create active sample warranties for customer@assurex.com."""
    from datetime import date, timedelta
    customer = db.query(User).filter(User.email == "customer@assurex.com").first()
    if not customer:
        return

    # Check if customer already has warranties
    existing_warranties = db.query(Warranty).join(Product, Warranty.product_id == Product.id).filter(Product.owner_id == customer.id).all()
    if existing_warranties:
        print("[OK] Demo customer already has warranties")
        return

    # Give demo customer 2 active warranties
    tv_prod = Product(
        product_id="PRD-DEMO-CUST-01",
        owner_id=customer.id,
        name='Samsung 65" 4K Neo QLED TV',
        category="electronics",
        brand="Samsung",
        model_number="QN65QN90C",
        serial_number="ELC-SAM-904751",
        purchase_date=date.today() - timedelta(days=90),
        purchase_price=218000,
        retailer="Samsung Official Flagship Store",
        warranty_duration_months=24,
        warranty_type="standard",
        warranty_start_date=date.today() - timedelta(days=90),
        warranty_expiry_date=date.today() + timedelta(days=640),
    )
    db.add(tv_prod)
    db.flush()

    w1 = Warranty(
        product_id=tv_prod.id,
        provider="Samsung Electronics Care",
        start_date=date.today() - timedelta(days=90),
        expiry_date=date.today() + timedelta(days=640),
        coverage_conditions="Standard OEM 24-Month Comprehensive Matrix Coverage",
        exclusions="Physical glass breakage, liquid immersion",
        service_centers="Samsung Authorized Service Network",
    )
    db.add(w1)

    phone_prod = Product(
        product_id="PRD-DEMO-CUST-02",
        owner_id=customer.id,
        name="iPhone 15 Pro Max 256GB",
        category="mobile_phones",
        brand="Apple",
        model_number="A3106",
        serial_number="MPH-APP-884129",
        purchase_date=date.today() - timedelta(days=45),
        purchase_price=465000,
        retailer="iStore Authorized Reseller",
        warranty_duration_months=12,
        warranty_type="standard",
        warranty_start_date=date.today() - timedelta(days=45),
        warranty_expiry_date=date.today() + timedelta(days=320),
    )
    db.add(phone_prod)
    db.flush()

    w2 = Warranty(
        product_id=phone_prod.id,
        provider="AppleCare Protection",
        start_date=date.today() - timedelta(days=45),
        expiry_date=date.today() + timedelta(days=320),
        coverage_conditions="Apple Limited Warranty 1-Year Hardware Coverage",
        exclusions="Accidental drop, liquid damage, unauthorized repairs",
        service_centers="Apple Authorized Service Providers",
    )
    db.add(w2)

    db.commit()
    print("[OK] Created 2 sample active warranties for customer@assurex.com")


def main():
    """Main seed function."""
    print("=" * 60)
    print("AssureX Database Seeding")
    print("=" * 60)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    print("[OK] Database tables created/verified")
    
    db = SessionLocal()
    try:
        create_admin_user(db)
        create_demo_users(db)
        create_sample_products(db)
        create_sample_warranties_for_demo_customer(db)
        create_model_version_entry(db)
        create_policies(db)
        
        print("\n[OK] Database seeding complete!")
        print("\nDemo Credentials:")
        print("  Admin:     admin@assurex.com / admin123")
        print("  Customer:  customer@assurex.com / customer123")
        print("  Staff:     staff@assurex.com / staff123")
        print("  Reviewer:  reviewer@assurex.com / reviewer123")
        
    finally:
        db.close()


if __name__ == "__main__":
    main()