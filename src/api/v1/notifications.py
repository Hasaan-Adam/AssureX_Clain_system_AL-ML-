"""
AssureX Claim Engine - Notifications API Router
Handles in-app notification queries, read status toggling, and bulk mark as read.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from database.session import get_db
from src.dependencies import get_current_user
from src.models.user import User
from src.schemas.notification import (
    MarkReadRequest,
    NotificationListResponse,
    NotificationResponse,
)
from src.services import notification_service

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=NotificationListResponse)
@router.get("/", response_model=NotificationListResponse)
def list_notifications(
    unread_only: bool = Query(False, description="Filter for unread notifications only"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve in-app notifications for the authenticated user."""
    items, total, unread_count = notification_service.get_user_notifications(
        db=db,
        user_id=current_user.id,
        unread_only=unread_only,
        skip=skip,
        limit=limit,
    )
    return {"total": total, "unread_count": unread_count, "notifications": items}


@router.put("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark a single notification as read."""
    return notification_service.mark_notification_as_read(
        db=db,
        notification_id=notification_id,
        user_id=current_user.id,
    )


@router.put("/read-all")
def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark all unread notifications as read for current user."""
    count = notification_service.mark_all_notifications_as_read(
        db=db,
        user_id=current_user.id,
    )
    return {"success": True, "marked_count": count}
