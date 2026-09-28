"""
Unit and API Integration tests for User Registration, Authentication, JWT Token Issuance, and Verification.
"""

import pytest
from src.core.security import decode_token, verify_password


def test_user_registration(client):
    """Test registering a new customer account."""
    payload = {
        "email": "newuser@example.com",
        "password": "SecurePassword123!",
        "full_name": "New User",
        "phone": "+1-555-0199",
        "role": "customer",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["full_name"] == "New User"
    assert data["role"] == "customer"
    assert data["is_active"] is True
    assert "id" in data


def test_duplicate_registration_fails(client, customer_user):
    """Attempting to register with existing email returns 409 conflict."""
    payload = {
        "email": customer_user.email,
        "password": "AnyPassword123!",
        "full_name": "Duplicate Person",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CONFLICT"


def test_login_success(client, customer_user):
    """Test successful login with email and password returning JWT tokens."""
    payload = {
        "email": customer_user.email,
        "password": "Password123!",
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == customer_user.email

    payload_decoded = decode_token(data["access_token"])
    assert payload_decoded["sub"] == str(customer_user.id)
    assert payload_decoded["role"] == customer_user.role


def test_login_invalid_password(client, customer_user):
    """Test failed login with invalid credentials."""
    payload = {
        "email": customer_user.email,
        "password": "WrongPassword123!",
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_get_current_user_profile(client, customer_headers, customer_user):
    """Test retrieving authenticated user profile."""
    response = client.get("/api/v1/auth/me", headers=customer_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == customer_user.email
    assert data["id"] == customer_user.id


def test_refresh_token_flow(client, customer_user):
    """Test refreshing access token using valid refresh token."""
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": customer_user.email, "password": "Password123!"},
    )
    refresh_tok = login_res.json()["refresh_token"]

    refresh_res = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_tok},
    )
    assert refresh_res.status_code == 200
    new_data = refresh_res.json()
    assert "access_token" in new_data
    assert new_data["token_type"] == "bearer"


def test_expired_token_rejected(client, customer_user):
    """Test expired access token returns 401 Unauthorized."""
    from datetime import timedelta
    from src.core.security import create_access_token

    expired_tok = create_access_token(
        subject=customer_user.id,
        role=customer_user.role,
        expires_delta=timedelta(seconds=-10),
    )
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_tok}"})
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_invalid_signature_token_rejected(client, customer_user):
    """Test token signed with wrong secret key returns 401 Unauthorized."""
    from src.core.security import create_access_token

    fake_secret_tok = create_access_token(
        subject=customer_user.id,
        role=customer_user.role,
        secret_key="attacker-tampered-secret-key-12345",
    )
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {fake_secret_tok}"})
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_tampered_token_rejected(client, customer_token):
    """Test corrupted or tampered token string returns 401 Unauthorized."""
    tampered_tok = customer_token[:-5] + "XXXXX"
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {tampered_tok}"})
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_missing_and_malformed_auth_header(client):
    """Test missing or malformed Authorization header returns 401."""
    res_no_auth = client.get("/api/v1/auth/me")
    assert res_no_auth.status_code == 401

    res_malformed = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer not-a-valid-jwt"})
    assert res_malformed.status_code == 401


def test_refresh_with_expired_or_invalid_token_fails(client, customer_user):
    """Test refresh token endpoint rejects expired or invalid tokens."""
    from datetime import timedelta
    from src.core.security import create_refresh_token

    expired_ref = create_refresh_token(
        subject=customer_user.id,
        role=customer_user.role,
        expires_delta=timedelta(seconds=-10),
    )
    res_expired = client.post("/api/v1/auth/refresh", json={"refresh_token": expired_ref})
    assert res_expired.status_code == 401

    from src.core.security import create_access_token
    access_tok = create_access_token(subject=customer_user.id, role=customer_user.role)
    res_type_mismatch = client.post("/api/v1/auth/refresh", json={"refresh_token": access_tok})
    assert res_type_mismatch.status_code == 401


def test_inactive_user_access_blocked(client, test_db):
    """Test that deactivated users cannot authenticate or access endpoints."""
    from src.models.user import User
    from src.utils.constants import RoleEnum
    from src.core.security import hash_password, create_access_token

    inactive_user = User(
        email="inactive@assurex.com",
        password_hash=hash_password("Password123!"),
        full_name="Deactivated User",
        role=RoleEnum.CUSTOMER.value,
        is_active=False,
    )
    test_db.add(inactive_user)
    test_db.commit()
    test_db.refresh(inactive_user)

    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "inactive@assurex.com", "password": "Password123!"},
    )
    assert login_res.status_code == 401
    assert "inactive" in login_res.json()["error"]["message"].lower()

    token = create_access_token(subject=inactive_user.id, role=inactive_user.role)
    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 403