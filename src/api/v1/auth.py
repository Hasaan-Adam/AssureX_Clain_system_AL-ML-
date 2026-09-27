"""Authentication Endpoints - Register, Login, Token Refresh, Me"""

from __future__ import annotations

from datetime import timedelta
from typing import Annotated, Any, Dict, Optional, Union

from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.exceptions import AuthenticationError, ConflictError, ValidationError
from src.core.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from src.dependencies import get_current_user, get_db
from src.schemas.user import PasswordChangeRequest, UserCreate, UserOut, UserUpdate

router = APIRouter()


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    email: str
    role: str
    exp: int


class RefreshTokenRequest(BaseModel):
    refresh_token: Optional[str] = None


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """Register a new user account."""
    from src.services.user_service import create_user, get_user_by_email

    clean_email = str(user_in.email).lower().strip()
    existing = get_user_by_email(clean_email, db=db)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered. Please sign in instead."
        )

    try:
        user = create_user(user_in, db=db)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT if "already registered" in str(ve).lower() else status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Registration failed: {str(exc)}")

    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "phone": user.phone,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user,
    }


@router.post("/login")
async def login(request: Request, db: Session = Depends(get_db)):
    """Authenticate user and return access + refresh tokens (supports both JSON and Form Data)."""
    from src.services.user_service import get_user_by_email

    username = ""
    password = ""

    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            body = await request.json()
            username = body.get("email") or body.get("username") or ""
            password = body.get("password") or ""
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON format")
    else:
        try:
            form = await request.form()
            username = form.get("username") or form.get("email") or ""
            password = form.get("password") or ""
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid form data format")

    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email/username and password are required.",
        )

    user = get_user_by_email(str(username).strip(), db=db)
    if not user or not verify_password(password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is inactive or disabled. Contact administrator.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": str(user["id"]), "email": user["email"], "role": user["role"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = create_refresh_token(data={"sub": str(user["id"])})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "phone": user.get("phone"),
            "role": user["role"],
            "is_active": user["is_active"],
        },
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: Request,
    refresh_token: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Exchange refresh token for new access + refresh token pair."""
    from src.services.user_service import get_user_by_id

    token_str = refresh_token
    if not token_str:
        try:
            body = await request.json()
            token_str = body.get("refresh_token")
        except Exception:
            pass

    if not token_str:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token required")

    try:
        payload = decode_token(token_str, expected_type="refresh")
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid refresh token: {str(e)}")

    user = get_user_by_id(int(user_id), db=db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is inactive or disabled. Contact administrator.",
        )

    new_access = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    new_refresh = create_refresh_token(data={"sub": str(user.id)})

    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserOut)
def get_me(current_user: Annotated[Any, Depends(get_current_user)]):
    """Return currently authenticated user profile."""
    return current_user