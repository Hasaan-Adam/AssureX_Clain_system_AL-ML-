"""
Unit and API Integration tests for User Profile Updates, Password Changes, and Role Management.
"""

import pytest


def test_update_profile(client, customer_headers, customer_user):
    """Test user updating their profile info."""
    payload = {
        "full_name": "John Updated Customer",
        "phone": "+1-555-9876",
    }
    res = client.put("/api/v1/users/me", json=payload, headers=customer_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["full_name"] == "John Updated Customer"
    assert data["phone"] == "+1-555-9876"


def test_admin_list_users(client, admin_headers, customer_user):
    """Test admin listing all users."""
    res = client.get("/api/v1/users/", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1


def test_admin_update_user_role_and_status(client, admin_headers, customer_headers, customer_user):
    """Test admin changing role and status of user."""
    # Update role using the legacy alias - it must be stored canonically.
    role_res = client.put(
        f"/api/v1/users/{customer_user.id}/role",
        json={"role": "staff"},
        headers=admin_headers,
    )
    assert role_res.status_code == 200
    assert role_res.json()["role"] == "service_staff"

    # Update status
    status_res = client.put(
        f"/api/v1/users/{customer_user.id}/status",
        json={"is_active": False},
        headers=admin_headers,
    )
    assert status_res.status_code == 200
    assert status_res.json()["is_active"] is False

    # A deactivated account must no longer be able to call the API.
    blocked = client.get("/api/v1/auth/me", headers=customer_headers)
    assert blocked.status_code == 403


# --- Role Escalation & RBAC Boundary Protection Tests ---

def test_customer_cannot_list_users(client, customer_headers):
    """Customer role attempting to access user directory must be rejected with 403."""
    res = client.get("/api/v1/users/", headers=customer_headers)
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "FORBIDDEN"


def test_customer_cannot_update_roles(client, customer_headers, customer_user):
    """Customer attempting privilege escalation by changing roles must be rejected with 403."""
    res = client.put(
        f"/api/v1/users/{customer_user.id}/role",
        json={"role": "admin"},
        headers=customer_headers,
    )
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "FORBIDDEN"


def test_customer_cannot_modify_user_status(client, customer_headers, customer_user):
    """Customer attempting to modify user status must be rejected with 403."""
    res = client.put(
        f"/api/v1/users/{customer_user.id}/status",
        json={"is_active": False},
        headers=customer_headers,
    )
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "FORBIDDEN"


def test_reviewer_and_staff_cannot_manage_roles(client, reviewer_headers, staff_headers, customer_user):
    """Non-admin roles cannot mutate user roles or permissions."""
    # Reviewer
    res_rev = client.put(
        f"/api/v1/users/{customer_user.id}/role",
        json={"role": "admin"},
        headers=reviewer_headers,
    )
    assert res_rev.status_code == 403

    # Staff
    res_staff = client.put(
        f"/api/v1/users/{customer_user.id}/role",
        json={"role": "admin"},
        headers=staff_headers,
    )
    assert res_staff.status_code == 403


def test_customer_cannot_access_admin_endpoints(client, customer_headers, reviewer_headers):
    """Ensure non-admins cannot access /api/v1/admin routes."""
    res_cust = client.get("/api/v1/admin/audit-logs", headers=customer_headers)
    assert res_cust.status_code == 403

    res_rev = client.get("/api/v1/admin/audit-logs", headers=reviewer_headers)
    assert res_rev.status_code == 403


def test_customer_and_staff_cannot_mutate_review_queues(client, customer_headers, staff_headers):
    """Ensure customer and staff cannot view review queues or submit review decisions."""
    # Customer queue access
    res_cust_queue = client.get("/api/v1/reviews/queue", headers=customer_headers)
    assert res_cust_queue.status_code == 403

    # Staff decision submission
    decision_payload = {
        "decision": "APPROVED",
        "reasoning": "Manual test override",
        "notes": "Attempted unauthorized decision",
    }
    res_staff_dec = client.post("/api/v1/reviews/1/decision", json=decision_payload, headers=staff_headers)
    assert res_staff_dec.status_code == 403

    # Customer decision submission
    res_cust_dec = client.post("/api/v1/reviews/1/decision", json=decision_payload, headers=customer_headers)
    assert res_cust_dec.status_code == 403