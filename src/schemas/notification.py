"""
AssureX Claim Engine - Notification Pydantic Schemas
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class NotificationBase(BaseModel):
    title: str = Field(..., max_length=255)
    message: str
    notification_type: str = Field("system_alert", max_length=50)
    channel: str = Field("in_app", max_length=50)
    severity: str = Field("INFO", max_length=20)
    metadata_json: Optional[Dict[str, Any]] = None


class NotificationCreate(NotificationBase):
    user_id: int


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    notification_type: Optional[str] = "system_alert"
    channel: Optional[str] = "in_app"
    severity: Optional[str] = "INFO"
    is_read: bool = False
    metadata_json: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = {'from_attributes': True, 'protected_namespaces': ()}


class NotificationListResponse(BaseModel):
    total: int
    unread_count: int
    notifications: List[NotificationResponse]


class MarkReadRequest(BaseModel):
    notification_ids: Optional[List[int]] = None
