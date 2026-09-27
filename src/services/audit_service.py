"""Audit Service - Audit Logging"""

from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from database.models import AuditLog, User
from src.core.exceptions import NotFoundError


def log_action(
    db: Session,
    action: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    user_id: Optional[int] = None,
    old_values: Optional[Dict[str, Any]] = None,
    new_values: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> AuditLog:
    """Log an audit action."""
    audit = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        old_values=str(old_values) if old_values else None,
        new_values=str(new_values) if new_values else None,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    return audit


def list_audit_logs(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
):
    """List audit logs and return (items, total)."""
    query = db.query(AuditLog)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    if entity_id:
        query = query.filter(AuditLog.entity_id == entity_id)
    total = query.count()
    items = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    return items, total