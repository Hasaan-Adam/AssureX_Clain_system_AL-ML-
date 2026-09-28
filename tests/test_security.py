"""
Unit tests for AssureX Security, Core RBAC, Exceptions, Utilities, and Policy JSONs.
"""

import json
from datetime import date, timedelta
from pathlib import Path
import pytest

from src.config import settings
from src.core.exceptions import (
    AssureXBaseException,
    EntityNotFoundException,
    ForbiddenException,
    UnauthorizedException,
    ValidationException,
    format_error_response,
)
from src.core.permissions import (
    get_permissions_for_role,
    has_permission,
    is_role_at_least,
    require_permission,
    require_role,
)
from src.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
    verify_token,
)
from src.utils.constants import RoleEnum
from src.utils.dates import (
    calculate_warranty_expiry,
    days_between,
    is_warranty_active,
    parse_date,
    parse_datetime,
)
from src.utils.file_utils import (
    generate_unique_filename,
    sanitize_filename,
    validate_file_extension,
    validate_file_size,
    validate_mime_type,
)
from src.utils.hashing import hash_bytes, hash_string



def test_password_hashing_and_bcrypt_12_rounds():
    """Verify bcrypt hashing with 12 rounds cost factor and verification logic."""
    from src.core.security import pwd_context

    raw_pass = "Admin@12345"
    hashed = hash_password(raw_pass)
    assert hashed != raw_pass
    assert verify_password(raw_pass, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False

    assert "bcrypt" in pwd_context.schemes()
    parts = hashed.split("$")
    assert len(parts) >= 4
    assert parts[2] == "12", f"Expected 12 bcrypt rounds, got {parts[2]}"


def test_password_hashing_edge_cases():
    """Verify empty or None password handling."""
    with pytest.raises(ValueError):
        hash_password("")

    assert verify_password("", "somehash") is False
    assert verify_password("password", "") is False
    assert verify_password(None, "somehash") is False
    assert verify_password("password", None) is False


def test_jwt_token_flow():
    user_id = 42
    role = RoleEnum.REVIEWER.value
    token = create_access_token(subject=user_id, role=role)
    payload = decode_token(token)

    assert payload["sub"] == str(user_id)
    assert payload["role"] == role
    assert payload["type"] == "access"

    verified = verify_token(token, expected_type="access")
    assert verified["sub"] == str(user_id)


def test_jwt_token_expiration():
    """Verify expired token raises UnauthorizedException."""
    token = create_access_token(subject=1, role="customer", expires_delta=timedelta(seconds=-10))
    with pytest.raises(UnauthorizedException) as exc_info:
        decode_token(token)
    assert "expired" in str(exc_info.value.message).lower()

    with pytest.raises(UnauthorizedException):
        verify_token(token, expected_type="access")


def test_jwt_invalid_signature_and_malformed():
    """Verify tokens with wrong signatures or malformed contents are rejected."""
    token = create_access_token(subject=1, role="customer", secret_key="wrong-secret-key-123")
    with pytest.raises(UnauthorizedException):
        decode_token(token)

    with pytest.raises(UnauthorizedException):
        decode_token("completely.invalid.jwttokenpayload")


def test_jwt_invalid_token_type():
    token = create_access_token(subject=1, role="customer")
    with pytest.raises(UnauthorizedException):
        verify_token(token, expected_type="refresh")



def test_four_role_rbac_matrix_permissions():
    """Rigorously verify permission matrix across customer, staff, reviewer, admin."""
    assert has_permission("customer", "claims:create") is True
    assert has_permission("customer", "claims:read_own") is True
    assert has_permission("customer", "claims:upload_docs") is True
    assert has_permission("customer", "warranties:register") is True
    assert has_permission("customer", "claims:approve") is False
    assert has_permission("customer", "claims:reject") is False
    assert has_permission("customer", "claims:read_all") is False
    assert has_permission("customer", "users:read") is False
    assert has_permission("customer", "users:manage_roles") is False
    assert has_permission("customer", "settings:update") is False

    assert has_permission("staff", "claims:create") is True
    assert has_permission("staff", "claims:read_all") is True
    assert has_permission("staff", "claims:create_on_behalf") is True
    assert has_permission("staff", "repairs:create") is True
    assert has_permission("staff", "repairs:update_status") is True
    assert has_permission("staff", "claims:approve") is False
    assert has_permission("staff", "claims:override_ai") is False
    assert has_permission("staff", "users:delete") is False
    assert has_permission("staff", "settings:update") is False

    assert has_permission("reviewer", "claims:review") is True
    assert has_permission("reviewer", "claims:approve") is True
    assert has_permission("reviewer", "claims:reject") is True
    assert has_permission("reviewer", "claims:escalate") is True
    assert has_permission("reviewer", "claims:override_ai") is True
    assert has_permission("reviewer", "predictions:read") is True
    assert has_permission("reviewer", "repairs:create") is True  # inherited
    assert has_permission("reviewer", "users:delete") is False
    assert has_permission("reviewer", "users:manage_roles") is False
    assert has_permission("reviewer", "settings:update") is False

    assert has_permission("admin", "users:create") is True
    assert has_permission("admin", "users:read") is True
    assert has_permission("admin", "users:update") is True
    assert has_permission("admin", "users:delete") is True
    assert has_permission("admin", "users:manage_roles") is True
    assert has_permission("admin", "claims:approve") is True
    assert has_permission("admin", "settings:read") is True
    assert has_permission("admin", "settings:update") is True
    assert has_permission("admin", "audit:export") is True
    assert has_permission("admin", "system:db_maintenance") is True
    assert has_permission("admin", "any_custom_permission_xyz") is True


def test_require_permission_guard():
    require_permission("staff", "repairs:create")
    with pytest.raises(ForbiddenException):
        require_permission("customer", "repairs:create")
    with pytest.raises(ForbiddenException):
        require_permission("customer", "users:manage_roles")
    with pytest.raises(ForbiddenException):
        require_permission("staff", "claims:approve")


def test_role_rank_hierarchy():
    assert is_role_at_least("admin", "admin") is True
    assert is_role_at_least("admin", "reviewer") is True
    assert is_role_at_least("admin", "staff") is True
    assert is_role_at_least("admin", "customer") is True

    assert is_role_at_least("reviewer", "reviewer") is True
    assert is_role_at_least("reviewer", "staff") is True
    assert is_role_at_least("reviewer", "customer") is True
    assert is_role_at_least("reviewer", "admin") is False

    assert is_role_at_least("staff", "staff") is True
    assert is_role_at_least("staff", "customer") is True
    assert is_role_at_least("staff", "reviewer") is False
    assert is_role_at_least("staff", "admin") is False

    assert is_role_at_least("customer", "customer") is True
    assert is_role_at_least("customer", "staff") is False
    assert is_role_at_least("customer", "reviewer") is False
    assert is_role_at_least("customer", "admin") is False



def test_error_formatting():
    resp = format_error_response(
        status_code=404,
        code="NOT_FOUND",
        message="Item not found",
        details={"id": 10},
    )
    assert resp.status_code == 404
    body = json.loads(resp.body.decode("utf-8"))
    assert body["success"] is False
    assert body["error"]["code"] == "NOT_FOUND"
    assert body["error"]["message"] == "Item not found"



def test_date_utilities():
    d = parse_date("2024-05-15")
    assert d == date(2024, 5, 15)

    expiry = calculate_warranty_expiry("2024-01-31", 12)
    assert expiry == date(2025, 1, 31)

    active, remaining = is_warranty_active("2024-01-01", "2024-12-31", "2024-06-01")
    assert active is True
    assert remaining > 0


def test_file_utilities():
    assert sanitize_filename("../../malicious/path.pdf") == "path.pdf"
    unique = generate_unique_filename("invoice.pdf", prefix="inv")
    assert unique.startswith("inv_")
    assert unique.endswith(".pdf")

    valid_ext, ext = validate_file_extension("receipt.PNG")
    assert valid_ext is True
    assert ext == ".png"

    assert validate_mime_type("application/pdf") is True
    assert validate_mime_type("application/x-msdownload") is False

    assert validate_file_size(1024) is True
    assert validate_file_size(20 * 1024 * 1024) is False


def test_hashing_utilities():
    h1 = hash_string("AssureX Claim Engine")
    h2 = hash_bytes(b"AssureX Claim Engine")
    assert h1 == h2
    assert len(h1) == 64



def test_policy_json_files_exist_and_valid():
    policy_files = ["policies/electronics.json", "policies/home_appliances.json", "policies/mobile_phones.json"]
    for pf in policy_files:
        path = Path(pf)
        assert path.exists(), f"Policy file {pf} must exist"
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert "category_code" in data
            assert "coverage" in data
            assert "allowed_fault_types" in data
            assert "exclusions" in data
            assert len(data["allowed_fault_types"]) > 0
            assert len(data["exclusions"]) > 0