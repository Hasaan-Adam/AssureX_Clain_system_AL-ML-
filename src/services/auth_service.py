"""
AssureX Claim Engine - Authentication & Token Issuance Service
Handles registration, password hashing, JWT lifecycle, and audit logging for security events.
"""

from typing import Any, Dict, Optional
from sqlalchemy.orm import Session

from src.core.exceptions import ConflictError, UnauthorizedException
from src.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from database.models import User, UserRole
from src.schemas.user import UserCreate
from src.services.audit_service import log_action


def register_user(
    db: Session,
    user_data: UserCreate,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> User:
    """Register a new user account with secure password hashing."""
    existing_user = db.query(User).filter(User.email == user_data.email.lower().strip()).first()
    if existing_user:
        from src.core.exceptions import ConflictError
        raise ConflictError(f"User with email '{user_data.email}' already exists.")

    role = (user_data.role or UserRole.CUSTOMER.value).lower().strip()
    if role not in [r.value for r in UserRole]:
        role = UserRole.CUSTOMER.value

    hashed_pw = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email.lower().strip(),
        hashed_password=hashed_pw,
        full_name=user_data.full_name.strip(),
        phone=user_data.phone.strip() if user_data.phone else None,
        role=role,
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    log_action(
        db=db,
        action="USER_REGISTER",
        entity_type="User",
        entity_id=str(new_user.id),
        user_id=new_user.id,
        new_values={"email": new_user.email, "role": new_user.role},
        ip_address=ip_address,
        user_agent=user_agent,
    )

    return new_user


def authenticate_user(
    db: Session,
    email: str,
    password: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> User:
    """Verify user credentials and return the active User record."""
    user = db.query(User).filter(User.email == email.lower().strip()).first()
    if not user or not verify_password(password, user.hashed_password):
        from src.core.exceptions import UnauthorizedException
        raise UnauthorizedException("Invalid email or password.")

    if not user.is_active:
        from src.core.exceptions import UnauthorizedException
        raise UnauthorizedException("User account is inactive or disabled.")

    log_action(
        db=db,
        action="USER_LOGIN",
        entity_type="User",
        entity_id=str(user.id),
        user_id=user.id,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    return user


def create_user_tokens(user: User) -> Dict[str, Any]:
    """Issue access and refresh JWT tokens for an authenticated user."""
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role},
    )
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 3600,
    }


def refresh_access_token(db: Session, refresh_token_str: str) -> Dict[str, Any]:
    """Validate refresh token and issue a fresh access token."""
    payload = decode_token(refresh_token_str)
    if payload.get("type") != "refresh":
        from src.core.exceptions import UnauthorizedException
        raise UnauthorizedException("Invalid refresh token type.")
    
    user_id_str = payload.get("sub")
    if not user_id_str:
        from src.core.exceptions import UnauthorizedException
        raise UnauthorizedException("Invalid refresh token payload.")

    user = db.query(User).filter(User.id == int(user_id_str)).first()
    if not user or not user.is_active:
        from src.core.exceptions import UnauthorizedException
        raise UnauthorizedException("User no longer exists or is inactive.")

    new_access_token = create_access_token(data={"sub": str(user.id), "email": user.email, "role": user.role})
    return {
        "access_token": new_access_token,
        "refresh_token": refresh_token_str,
        "token_type": "bearer",
        "expires_in": 3600,
    }


def validate_token(token_str: str) -> Dict[str, Any]:
    """Decode and return token payload."""
    return decode_token(token_str)