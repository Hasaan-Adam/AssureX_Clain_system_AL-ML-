"""
AssureX Claim Engine - Users & Profiles API Router
Handles user profile updates, administrative user listing, role modifications, and status controls.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from database.session import get_db
from src.dependencies import get_current_user, require_role
from src.models.user import User
from src.schemas.user import (
    RoleUpdatePayload,
    StatusUpdatePayload,
    UserListResponse,
    UserProfileUpdate,
    UserResponse,
)
from src.services import user_service
from src.utils.constants import RoleEnum

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user),
):
    """Retrieve currently authenticated user's profile."""
    return current_user


@router.put("/me", response_model=UserResponse)
def update_my_profile(
    update_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update profile information (name, phone) for current user."""
    return user_service.update_user(
        db=db,
        user_id=current_user.id,
        user_update=update_data,
    )


@router.get("", response_model=UserListResponse, dependencies=[Depends(require_role("admin"))])
@router.get("/", response_model=UserListResponse, dependencies=[Depends(require_role("admin"))])
def list_all_users(
    role: Optional[str] = Query(None, description="Filter by role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search by email or name"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Admin endpoint to list all users with filtering and pagination."""
    users, total = user_service.list_users(
        db=db,
        role=role,
        is_active=is_active,
        search=search,
        skip=skip,
        limit=limit,
    )
    return {"total": total, "users": users}


@router.get("/{user_id}", response_model=UserResponse, dependencies=[Depends(require_role("admin"))])
def get_user_details(
    user_id: int,
    db: Session = Depends(get_db),
):
    """Admin endpoint to view a specific user's details."""
    return user_service.get_user_by_id(user_id, db=db)


@router.put("/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: int,
    payload: RoleUpdatePayload,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Admin endpoint to modify a user's role."""
    from src.schemas.user import UserUpdate
    return user_service.update_user(
        user_id=user_id,
        user_update=UserUpdate(role=payload.role),
        db=db,
    )


@router.put("/{user_id}/status", response_model=UserResponse)
def update_user_status(
    user_id: int,
    payload: StatusUpdatePayload,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Admin endpoint to activate or deactivate a user account."""
    from src.schemas.user import UserUpdate
    return user_service.update_user(
        user_id=user_id,
        user_update=UserUpdate(is_active=payload.is_active),
        db=db,
    )

