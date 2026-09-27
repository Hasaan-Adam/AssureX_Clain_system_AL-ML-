"""Notification Service - User Notifications"""

from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from database.models import Notification, User
from src.core.exceptions import NotFoundError


def create_notification(
    db: Session,
    user_id: int,
    title: str,
    message: str,
    type: str = "in_app",
    related_entity_type: Optional[str] = None,
    related_entity_id: Optional[str] = None,
) -> Notification:
    """Create a notification."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundError("User", user_id)
    
    notif = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=type,
        related_entity_type=related_entity_type,
        related_entity_id=related_entity_id,
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif


def get_user_notifications(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 20,
    unread_only: bool = False,
):
    """Get user notifications with total and unread counts."""
    base_query = db.query(Notification).filter(Notification.user_id == user_id)
    total = base_query.count()
    unread_count = base_query.filter(Notification.is_read == False).count()
    
    query = base_query
    if unread_only:
        query = query.filter(Notification.is_read == False)
    items = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
    return items, total, unread_count


def mark_notification_as_read(db: Session, notification_id: int, user_id: int) -> Notification:
    notif = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == user_id
    ).first()
    if not notif:
        raise NotFoundError("Notification", notification_id)
    
    notif.is_read = True
    notif.read_at = datetime.utcnow()
    db.commit()
    db.refresh(notif)
    return notif


def mark_all_notifications_as_read(db: Session, user_id: int) -> int:
    result = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == False
    ).update({"is_read": True, "read_at": datetime.utcnow()})
    db.commit()
    return result


def notify_all_reviewers(db: Session, title: str, message: str, related_entity_type: Optional[str] = None, related_entity_id: Optional[str] = None) -> List[Notification]:
    """Notify all reviewers."""
    reviewers = db.query(User).filter(User.role == "reviewer").all()
    notifications = []
    for reviewer in reviewers:
        notif = create_notification(db, reviewer.id, title, message, "in_app", related_entity_type, related_entity_id)
        notifications.append(notif)
    return notifications