"""
Unit and API Integration tests for Notifications, Read Status Toggling, and Expiry Reminders.
"""

import pytest
from src.services.notification_service import create_notification


def test_notification_lifecycle(client, test_db, customer_headers, customer_user):
    """Test creating notification, retrieving it, and marking it as read."""
    notif = create_notification(
        db=test_db,
        user_id=customer_user.id,
        title="Test Alert",
        message="This is a test notification.",
    )

    res = client.get("/api/v1/notifications/", headers=customer_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    assert data["unread_count"] >= 1

    read_res = client.put(f"/api/v1/notifications/{notif.id}/read", headers=customer_headers)
    assert read_res.status_code == 200
    assert read_res.json()["is_read"] is True

    all_read_res = client.put("/api/v1/notifications/read-all", headers=customer_headers)
    assert all_read_res.status_code == 200