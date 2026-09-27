"""User Service - Account Management, Authentication, Profile"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from sqlalchemy.orm import Session

from database.connection import SessionLocal
from database.models import User
from src.core.security import get_password_hash, verify_password
from src.schemas.user import UserCreate, UserOut, UserRole, UserUpdate
from src.services.audit_service import log_action
from src.utils.constants import normalize_role


def _get_db() -> Session:
    return SessionLocal()


def _close_if_owned(db: Session, owned: bool) -> None:
    if owned:
        db.close()


def _user_to_dict(user: User, include_password: bool = False) -> dict:
    d = {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "phone": user.phone,
        "profile_image_url": getattr(user, "profile_image_url", None),
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }
    if include_password:
        d["hashed_password"] = user.hashed_password
    return d


def create_user(user_in: UserCreate, db: Optional[Session] = None) -> UserOut:
    owned = db is None
    db = db or _get_db()
    try:
        existing = db.query(User).filter(User.email == user_in.email.lower().strip()).first()
        if existing:
            raise ValueError("Email already registered")
        
        role = normalize_role(user_in.role, default="customer") or "customer"
        
        hashed_pw = get_password_hash(user_in.password)
        new_user = User(
            email=user_in.email.lower().strip(),
            hashed_password=hashed_pw,
            full_name=user_in.full_name.strip(),
            phone=user_in.phone.strip() if user_in.phone else None,
            profile_image_url=getattr(user_in, "profile_image_url", None),
            role=role,
            is_active=True,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return UserOut(
            id=new_user.id,
            email=new_user.email,
            full_name=new_user.full_name,
            phone=new_user.phone,
            profile_image_url=new_user.profile_image_url,
            role=role,
            is_active=new_user.is_active,
            created_at=new_user.created_at,
            updated_at=new_user.updated_at,
        )
    finally:
        _close_if_owned(db, owned)


def get_user_by_email(email: str, db: Optional[Session] = None) -> Optional[dict]:
    owned = db is None
    db = db or _get_db()
    try:
        user = db.query(User).filter(User.email == email.lower().strip()).first()
        if user:
            return _user_to_dict(user, include_password=True)
        return None
    finally:
        _close_if_owned(db, owned)


def get_user_by_id(user_id: int, db: Optional[Session] = None) -> Optional[UserOut]:
    owned = db is None
    db = db or _get_db()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        role_val = normalize_role(user.role, default="customer") or "customer"
        return UserOut(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            profile_image_url=user.profile_image_url,
            role=role_val,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
    finally:
        _close_if_owned(db, owned)


def get_users(
    skip: int = 0,
    limit: int = 20,
    role: Optional[str] = None,
    db: Optional[Session] = None,
) -> List[UserOut]:
    owned = db is None
    db = db or _get_db()
    try:
        query = db.query(User)
        if role:
            query = query.filter(User.role == normalize_role(role, default=role))
        users = query.offset(skip).limit(limit).all()
        return [
            UserOut(
                id=u.id,
                email=u.email,
                full_name=u.full_name,
                phone=u.phone,
                profile_image_url=u.profile_image_url,
                role=normalize_role(u.role, default="customer"),
                is_active=u.is_active,
                created_at=u.created_at,
                updated_at=u.updated_at,
            )
            for u in users
        ]
    finally:
        _close_if_owned(db, owned)


def update_user(user_id: int, user_update: UserUpdate, db: Optional[Session] = None) -> UserOut:
    owned = db is None
    db = db or _get_db()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")

        update_data = user_update.model_dump(exclude_unset=True)
        if "role" in update_data and update_data["role"] is not None:
            update_data["role"] = normalize_role(update_data["role"], default="customer")
        previous_role = user.role
        for field, value in update_data.items():
            setattr(user, field, value)

        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)

        if "role" in update_data and user.role != previous_role:
            log_action(
                db=db,
                action="USER_ROLE_CHANGE",
                entity_type="User",
                entity_id=str(user.id),
                user_id=user.id,
                old_values={"role": previous_role},
                new_values={"role": user.role},
            )

        return UserOut(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            profile_image_url=user.profile_image_url,
            role=normalize_role(user.role, default="customer"),
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
    finally:
        _close_if_owned(db, owned)


def deactivate_user(user_id: int, db: Optional[Session] = None) -> bool:
    owned = db is None
    db = db or _get_db()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        user.is_active = False
        user.updated_at = datetime.utcnow()
        db.commit()
        return True
    finally:
        _close_if_owned(db, owned)


def authenticate_user(email: str, password: str, db: Optional[Session] = None) -> Optional[dict]:
    user = get_user_by_email(email, db=db)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user


def change_password(user_id: int, current_password: str, new_password: str, db: Optional[Session] = None) -> bool:
    owned = db is None
    db = db or _get_db()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        if not verify_password(current_password, user.hashed_password):
            raise ValueError("Current password is incorrect")
        
        user.hashed_password = get_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        db.commit()
        return True
    finally:
        _close_if_owned(db, owned)


def list_users(
    db: Optional[Session] = None,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
):
    """List users with filtering, searching, and pagination."""
    owned = db is None
    session = db or _get_db()
    try:
        query = session.query(User)
        if role:
            query = query.filter(User.role == normalize_role(role, default=str(role).lower()))
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        if search:
            search_pat = f"%{search}%"
            query = query.filter((User.email.ilike(search_pat)) | (User.full_name.ilike(search_pat)))
            
        total = query.count()
        users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
        user_outs = [
            UserOut(
                id=u.id,
                email=u.email,
                full_name=u.full_name,
                phone=u.phone,
                profile_image_url=u.profile_image_url,
                role=normalize_role(u.role, default="customer") or "customer",
                is_active=u.is_active,
                created_at=u.created_at,
                updated_at=u.updated_at,
            )
            for u in users
        ]
        return user_outs, total
    finally:
        _close_if_owned(session, owned)

def update_profile(user_id: int, user_update: UserUpdate, db: Optional[Session] = None) -> UserOut:
    return update_user(user_id, user_update, db)

def update_user_role(user_id: int, user_update: UserUpdate, db: Optional[Session] = None) -> UserOut:
    return update_user(user_id, user_update, db)

def update_user_status(user_id: int, db: Optional[Session] = None) -> bool:
    return deactivate_user(user_id, db)

# Database seeding function (call explicitly from seed script or app startup)
def seed_database():
    """Seed database with default users if not already present."""
    db = SessionLocal()
    try:
        # Check if admin user exists
        admin = db.query(User).filter(User.email == "admin@assurex.com").first()
        if not admin:
            from src.core.security import get_password_hash
            admin = User(
                email="admin@assurex.com",
                hashed_password=get_password_hash("admin123"),
                full_name="System Administrator",
                phone="+92-300-1234567",
                role="admin",
                is_active=True,
            )
            db.add(admin)
            
            # Create demo users
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
            
            db.commit()
            print("[OK] Database seeded with demo users")
        else:
            print("[OK] Database already seeded")
    finally:
        db.close()