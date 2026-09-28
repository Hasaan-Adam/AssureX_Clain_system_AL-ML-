"""User Schemas - Pydantic models for User API"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from src.utils.constants import ROLE_ALIASES
from src.utils.constants import RoleEnum as UserRole


def _coerce_role(value: Any) -> UserRole:
    """Map any accepted role spelling onto the canonical UserRole member."""
    if isinstance(value, UserRole):
        return value
    raw = str(value).lower().strip()
    for role in UserRole:
        if role.value == raw:
            return role
    canonical = ROLE_ALIASES.get(raw)
    if canonical:
        return UserRole(canonical)
    return UserRole.CUSTOMER


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    phone: Optional[str] = None
    profile_image_url: Optional[str] = None
    role: UserRole = UserRole.CUSTOMER

    @field_validator("phone", mode="before")
    @classmethod
    def clean_phone(cls, v: Any) -> Optional[str]:
        if not v or not str(v).strip():
            return None
        return str(v).strip()

    @field_validator("role", mode="before")
    @classmethod
    def clean_role(cls, v: Any) -> UserRole:
        return _coerce_role(v)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=72)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, pattern=r"^\+?[\d\s\-\(\)]{7,20}$")
    profile_image_url: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None

    @field_validator("role", mode="before")
    @classmethod
    def clean_role(cls, v: Any) -> Optional[UserRole]:
        if v is None:
            return None
        return _coerce_role(v)


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    profile_image_url: Optional[str] = None
    role: UserRole = UserRole.CUSTOMER
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    @field_validator("role", mode="before")
    @classmethod
    def clean_role(cls, v: Any) -> UserRole:
        return _coerce_role(v)

    model_config = {'from_attributes': True}


UserResponse = UserOut


class UserInDBBase(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    phone: Optional[str]
    role: UserRole
    is_active: bool
    hashed_password: str
    created_at: datetime
    updated_at: datetime

    model_config = {'from_attributes': True}


class TokenPayload(BaseModel):
    sub: str
    email: str
    role: str
    exp: int


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=72)

class RoleUpdatePayload(BaseModel):
    role: UserRole

    @field_validator("role", mode="before")
    @classmethod
    def clean_role(cls, v: Any) -> Any:
        """Accept legacy aliases (e.g. "staff") and store the canonical role."""
        if v is None:
            return None
        return _coerce_role(v)

class StatusUpdatePayload(BaseModel):
    is_active: bool

class TokenRefreshRequest(BaseModel):
    refresh_token: str

class TokenRefreshResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, pattern=r"^\+?[\d\s\-\(\)]{7,20}$")
    profile_image_url: Optional[str] = None

class UserListResponse(BaseModel):
    users: list[UserOut]
    total: int
    page: int = 1
    page_size: int = 50