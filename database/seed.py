"""
Database Seed Script - Creates demo users on first startup.
Only creates users if they don't already exist.
"""

from database.connection import SessionLocal
from database.models import User
from src.core.security import get_password_hash


DEMO_USERS = [
    {
        "email": "customer@assurex.com",
        "full_name": "Demo Customer",
        "phone": "+92-300-1234567",
        "role": "customer",
        "password": "customer123",
    },
    {
        "email": "reviewer@assurex.com",
        "full_name": "Demo Reviewer",
        "phone": "+92-300-2345678",
        "role": "reviewer",
        "password": "reviewer123",
    },
    {
        "email": "admin@assurex.com",
        "full_name": "Demo Administrator",
        "phone": "+92-300-3456789",
        "role": "admin",
        "password": "admin123",
    },
    {
        "email": "staff@assurex.com",
        "full_name": "Demo Staff Support",
        "phone": "+92-300-4567890",
        "role": "service_staff",
        "password": "staff123",
    },
]


def seed_demo_users():
    """Create demo users if they don't exist yet."""
    db = SessionLocal()
    try:
        created = 0
        for user_data in DEMO_USERS:
            existing = db.query(User).filter(User.email == user_data["email"]).first()
            if existing:
                continue

            user = User(
                email=user_data["email"],
                full_name=user_data["full_name"],
                phone=user_data["phone"],
                role=user_data["role"],
                hashed_password=get_password_hash(user_data["password"]),
                is_active=True,
            )
            db.add(user)
            created += 1

        if created > 0:
            db.commit()
            print(f"[SEED] Created {created} demo user(s).")
        else:
            print("[SEED] All demo users already exist. Skipping.")
    except Exception as e:
        db.rollback()
        print(f"[SEED] Error seeding users: {e}")
    finally:
        db.close()