"""
Audit script for Auth and Profile workflows:
1. Test POST /api/v1/auth/login with valid admin, reviewer, and customer credentials.
2. Test POST /api/v1/auth/register with a new test user.
3. Test GET /api/v1/users/me with valid bearer token.
4. Verify all payload structures and user response schemas.
"""

import os
import sys

sys.path.insert(0, os.path.abspath("."))

from fastapi.testclient import TestClient
from src.main import app
from database.session import get_db_context
from database.seed import seed_database
from src.models.user import User

def run_audit():
    print("=" * 60)
    print("STARTING AUTH & PROFILE WORKFLOW AUDIT")
    print("=" * 60)

    # Ensure database is seeded
    seed_database()
    
    client = TestClient(app)

    # -------------------------------------------------------------
    # 1. Test POST /api/v1/auth/login with admin, reviewer, customer
    # -------------------------------------------------------------
    accounts = [
        ("Admin", "admin@assurex.com", "Admin@12345", "admin"),
        ("Reviewer", "reviewer@assurex.com", "Reviewer@12345", "reviewer"),
        ("Customer", "customer@assurex.com", "Customer@12345", "customer"),
    ]

    tokens = {}

    print("\n--- STEP 1: Testing POST /api/v1/auth/login ---")
    for role_name, email, password, expected_role in accounts:
        payload = {"email": email, "password": password}
        resp = client.post("/api/v1/auth/login", json=payload)
        print(f"[{role_name} Login] Status: {resp.status_code}")
        assert resp.status_code == 200, f"Login failed for {role_name}: {resp.text}"
        data = resp.json()
        assert "access_token" in data, f"Missing access_token for {role_name}"
        assert "refresh_token" in data, f"Missing refresh_token for {role_name}"
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == email
        assert data["user"]["role"] == expected_role
        tokens[role_name] = data["access_token"]
        print(f"  -> SUCCESS: Received bearer token for {role_name} (User: {data['user']['full_name']}, Role: {data['user']['role']})")

    # -------------------------------------------------------------
    # 2. Test POST /api/v1/auth/register with new test user
    # -------------------------------------------------------------
    print("\n--- STEP 2: Testing POST /api/v1/auth/register ---")
    new_user_email = f"audit_user_{sys.version_info.major}{sys.version_info.minor}@example.com"
    
    # Cleanup previous test run user if present
    with get_db_context() as db:
        old_user = db.query(User).filter(User.email == new_user_email).first()
        if old_user:
            db.delete(old_user)
            db.commit()

    reg_payload = {
        "email": new_user_email,
        "password": "Password123!",
        "full_name": "Audit Test Customer",
        "phone": "+1-555-888-9999",
        "role": "customer"
    }
    reg_resp = client.post("/api/v1/auth/register", json=reg_payload)
    print(f"[Register New User] Status: {reg_resp.status_code}")
    assert reg_resp.status_code == 201, f"Register failed: {reg_resp.text}"
    reg_data = reg_resp.json()
    assert reg_data["email"] == new_user_email
    assert reg_data["full_name"] == "Audit Test Customer"
    assert reg_data["role"] == "customer"
    assert reg_data["is_active"] is True
    assert "id" in reg_data
    print(f"  -> SUCCESS: Registered new user ID {reg_data['id']}, email: {reg_data['email']}")

    # Login with newly registered user
    new_login_resp = client.post("/api/v1/auth/login", json={"email": new_user_email, "password": "Password123!"})
    assert new_login_resp.status_code == 200
    tokens["NewUser"] = new_login_resp.json()["access_token"]
    print(f"  -> SUCCESS: Successfully authenticated newly registered user")

    # -------------------------------------------------------------
    # 3. Test GET /api/v1/users/me with valid bearer token
    # -------------------------------------------------------------
    print("\n--- STEP 3: Testing GET /api/v1/users/me ---")
    for user_key, bearer_token in tokens.items():
        headers = {"Authorization": f"Bearer {bearer_token}"}
        me_resp = client.get("/api/v1/users/me", headers=headers)
        print(f"[{user_key} GET /api/v1/users/me] Status: {me_resp.status_code}")
        assert me_resp.status_code == 200, f"GET /api/v1/users/me failed for {user_key}: {me_resp.text}"
        me_data = me_resp.json()
        assert "id" in me_data
        assert "email" in me_data
        assert "full_name" in me_data
        assert "role" in me_data
        assert "is_active" in me_data
        print(f"  -> SUCCESS: Retrieved profile for {user_key}: ID={me_data['id']}, Name='{me_data['full_name']}', Role='{me_data['role']}'")

    print("\n" + "=" * 60)
    print("ALL BACKEND AUTH & PROFILE WORKFLOW TESTS PASSED!")
    print("=" * 60)

if __name__ == "__main__":
    run_audit()
