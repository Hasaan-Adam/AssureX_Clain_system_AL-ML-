"""FastAPI Dependencies - Database, Auth, RBAC, Request Context"""

from __future__ import annotations

from typing import Annotated, Generator, Optional

from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.connection import SessionLocal
from database.session import get_db  # single source of truth so test overrides apply
from src.core.config import settings
from src.core.exceptions import AuthenticationError, AuthorizationError
from src.core.security import ALGORITHM, SECRET_KEY, decode_token
from src.schemas.user import UserOut, UserRole
from src.utils.constants import PRIVILEGED_ROLES, RoleEnum, normalize_role


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
optional_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


class TokenData(BaseModel):
    sub: str
    email: str
    role: str
    exp: int


__all__ = [
    "get_db",
    "get_current_user",
    "get_current_active_user",
    "require_role",
    "current_user_role",
    "is_privileged",
    "require_customer",
    "require_staff",
    "require_reviewer",
    "require_admin",
    "require_privileged",
    "get_request_id",
    "get_client_ip",
    "get_pagination",
    "PaginationParams",
    "oauth2_scheme",
    "TokenData",
]


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
) -> "UserOut":
    """Validate JWT access token and return current user."""
    from src.services.user_service import get_user_by_id

    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.security.secret_key, algorithms=[settings.security.algorithm])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = get_user_by_id(int(user_id), db=db)
    if not user:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Account is inactive or disabled. Contact administrator.",
        )

    return user


def get_current_active_user(
    current_user: Annotated["UserOut", Depends(get_current_user)],
) -> "UserOut":
    """Ensure user account is active (not disabled)."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_optional_user(
    token: Annotated[Optional[str], Depends(optional_oauth2_scheme)] = None,
    db: Session = Depends(get_db),
) -> Optional["UserOut"]:
    """
    Return the authenticated user when a valid token is supplied, otherwise
    ``None``. Never rejects anonymous callers; an invalid token is ignored so
    public endpoints stay reachable.
    """
    if not token:
        return None
    from src.services.user_service import get_user_by_id

    try:
        payload = jwt.decode(token, settings.security.secret_key, algorithms=[settings.security.algorithm])
        user_id = payload.get("sub")
        if not user_id:
            return None
    except Exception:
        return None

    user = get_user_by_id(int(user_id), db=db)
    if not user or not user.is_active:
        return None
    return user


def require_role(*allowed_roles: Any):
    """Dependency factory for role-based access control.

    Both sides of the comparison are normalised, so ``RoleEnum.SERVICE_STAFF``,
    ``"staff"`` and ``"service_staff"`` are all treated as the same role.
    """
    def role_checker(current_user: Annotated["UserOut", Depends(get_current_active_user)]) -> "UserOut":
        user_role_str = normalize_role(current_user.role, default="customer") or "customer"
        allowed_str = [
            normalize_role(r, default=str(r).lower()) for r in allowed_roles
        ]
        if user_role_str not in allowed_str:
            raise HTTPException(
                status_code=403,
                detail=f"Role {user_role_str} not authorized. Required: {allowed_str}",
            )
        return current_user
    return role_checker


def current_user_role(current_user: "UserOut") -> str:
    """Canonical role string of the authenticated user."""
    return normalize_role(current_user.role, default="customer") or "customer"


def is_privileged(current_user: "UserOut") -> bool:
    """True for service staff, reviewers and admins (cross-tenant visibility)."""
    return current_user_role(current_user) in PRIVILEGED_ROLES


require_customer = require_role("customer")
require_staff = require_role("service_staff", "reviewer", "admin")
require_reviewer = require_role("reviewer", "admin")
require_admin = require_role("admin")
require_privileged = require_role("service_staff", "reviewer", "admin")


def get_request_id(request: Request) -> str:
    """Extract or generate request ID for tracing."""
    return request.headers.get("X-Request-ID", __import__("uuid").uuid4().hex[:8])


def get_client_ip(request: Request) -> str:
    """Extract client IP from request headers or socket."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


class PaginationParams(BaseModel):
    page: int = 1
    page_size: int = 20

    def __init__(self, page: int = 1, page_size: int = 20):
        super().__init__(page=page, page_size=min(page_size, 100))


def get_pagination(params: Annotated[PaginationParams, Depends()]) -> PaginationParams:
    return params
