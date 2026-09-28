"""Security Utilities - JWT, Password Hashing, Token Management"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from jose import jwt, JWTError, ExpiredSignatureError
from passlib.context import CryptContext

from src.core.config import settings
from src.core.exceptions import AuthenticationError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

SECRET_KEY = settings.security.secret_key
ALGORITHM = settings.security.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.security.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = settings.security.refresh_token_expire_days


def verify_password(plain_password: Optional[str], hashed_password: Optional[str]) -> bool:
    """Verify a plain password against its hash safely."""
    if not plain_password or not hashed_password:
        return False
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Hash a password with bcrypt. Raises ValueError on empty password."""
    if not password:
        raise ValueError("Password cannot be empty")
    return pwd_context.hash(password)


def create_access_token(
    data: Optional[Dict[str, Any]] = None,
    subject: Optional[Any] = None,
    role: Optional[str] = None,
    expires_delta: Optional[timedelta] = None,
    secret_key: Optional[str] = None,
    **kwargs: Any,
) -> str:
    """Create a JWT access token."""
    to_encode = (data or {}).copy()
    if subject is not None:
        to_encode["sub"] = str(subject)
    if role is not None:
        to_encode["role"] = str(role.value if hasattr(role, 'value') else role)
    for k, v in kwargs.items():
        if k not in to_encode:
            to_encode[k] = v
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": to_encode.get("type", "access")})
    key = secret_key or SECRET_KEY
    return jwt.encode(to_encode, key, algorithm=ALGORITHM)


def create_refresh_token(
    data: Optional[Dict[str, Any]] = None,
    subject: Optional[Any] = None,
    role: Optional[str] = None,
    expires_delta: Optional[timedelta] = None,
    secret_key: Optional[str] = None,
    **kwargs: Any,
) -> str:
    """Create a JWT refresh token (longer expiry)."""
    to_encode = (data or {}).copy()
    if subject is not None:
        to_encode["sub"] = str(subject)
    if role is not None:
        to_encode["role"] = str(role.value if hasattr(role, 'value') else role)
    for k, v in kwargs.items():
        if k not in to_encode:
            to_encode[k] = v
    expire = datetime.utcnow() + (expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire, "type": "refresh"})
    key = secret_key or SECRET_KEY
    return jwt.encode(to_encode, key, algorithm=ALGORITHM)


def decode_token(token: str, expected_type: Optional[str] = None, secret_key: Optional[str] = None) -> Dict[str, Any]:
    """Decode and validate a JWT token. Raises AuthenticationError on invalid/expired tokens."""
    key = secret_key or SECRET_KEY
    try:
        payload = jwt.decode(token, key, algorithms=[ALGORITHM])
        if expected_type and payload.get("type") != expected_type:
            raise AuthenticationError(f"Invalid token type. Expected {expected_type}, got {payload.get('type')}")
        return payload
    except ExpiredSignatureError:
        raise AuthenticationError("Token has expired. Please log in again.")
    except (JWTError, Exception) as e:
        raise AuthenticationError(f"Could not validate credentials: {str(e)}")


def verify_token(token: str, expected_type: Optional[str] = None) -> Dict[str, Any]:
    """Verify token type and validity."""
    return decode_token(token, expected_type=expected_type)


def create_password_reset_token(email: str) -> str:
    """Create a short-lived password reset token."""
    expire = datetime.utcnow() + timedelta(minutes=settings.security.password_reset_token_expire_minutes)
    to_encode = {"sub": email, "type": "password_reset", "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_password_reset_token(token: str) -> Optional[str]:
    """Verify password reset token and return email."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "password_reset":
            return None
        return payload.get("sub")
    except JWTError:
        return None


hash_password = get_password_hash
UnauthorizedException = AuthenticationError