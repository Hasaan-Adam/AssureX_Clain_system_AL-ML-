"""
AssureX Claim Engine - Role-Based Access Control (RBAC) & Permissions
"""

from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Set
import yaml

from src.core.exceptions import ForbiddenException
from src.utils.constants import RoleEnum, normalize_role


DEFAULT_ROLE_HIERARCHY: Dict[str, Set[str]] = {
    RoleEnum.CUSTOMER.value: {
        "claims:create",
        "claims:read_own",
        "claims:update_own",
        "claims:upload_docs",
        "claims:appeal_own",
        "warranties:register",
        "warranties:read_own",
        "products:read",
        "notifications:read_own",
        "notifications:mark_read",
        "profile:read_own",
        "profile:update_own",
    },
    RoleEnum.SERVICE_STAFF.value: {
        "claims:read_all",
        "claims:create_on_behalf",
        "claims:add_notes",
        "warranties:read_all",
        "warranties:verify",
        "products:read",
        "repairs:read_all",
        "repairs:create",
        "repairs:update_status",
        "customers:read",
        "notifications:send",
    },
    RoleEnum.REVIEWER.value: {
        "claims:review",
        "claims:approve",
        "claims:reject",
        "claims:escalate",
        "claims:override_ai",
        "predictions:read",
        "predictions:evaluate",
        "policies:read",
        "audit:read_claims",
        "reports:read",
    },
    RoleEnum.ADMIN.value: {
        "users:create",
        "users:read",
        "users:update",
        "users:delete",
        "users:manage_roles",
        "products:create",
        "products:update",
        "products:delete",
        "policies:create",
        "policies:update",
        "policies:delete",
        "settings:read",
        "settings:update",
        "audit:read_all",
        "audit:export",
        "monitoring:read",
        "monitoring:manage_alerts",
        "system:db_maintenance",
        "reports:export",
    },
}

ROLE_RANK: Dict[str, int] = {
    RoleEnum.CUSTOMER.value: 10,
    RoleEnum.SERVICE_STAFF.value: 20,
    RoleEnum.REVIEWER.value: 30,
    RoleEnum.ADMIN.value: 100,
}


@lru_cache()
def load_roles_config(roles_file_path: Optional[str] = None) -> Dict[str, Set[str]]:
    """
    Load RBAC role permissions from YAML with inheritance resolution.
    """
    path = Path(roles_file_path) if roles_file_path else Path("config/roles.yaml")
    if not path.exists():
        merged: Dict[str, Set[str]] = {}
        for role, rank in sorted(ROLE_RANK.items(), key=lambda x: x[1]):
            role_perms = set(DEFAULT_ROLE_HIERARCHY.get(role, set()))
            if rank >= 20:
                role_perms |= DEFAULT_ROLE_HIERARCHY.get(RoleEnum.CUSTOMER.value, set())
            if rank >= 30:
                role_perms |= DEFAULT_ROLE_HIERARCHY.get(RoleEnum.SERVICE_STAFF.value, set())
            if rank >= 100:
                role_perms |= DEFAULT_ROLE_HIERARCHY.get(RoleEnum.REVIEWER.value, set())
            merged[role] = role_perms
        return merged

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        roles_data = data.get("roles", {})
        resolved: Dict[str, Set[str]] = {}

        def get_inherited_permissions(role_name: str, visited: Optional[Set[str]] = None) -> Set[str]:
            if visited is None:
                visited = set()
            if role_name in visited:
                return set()
            visited.add(role_name)

            role_spec = roles_data.get(role_name, {})
            perms = set(role_spec.get("permissions", []))
            for parent in role_spec.get("inherits", []):
                perms |= get_inherited_permissions(parent, visited)
            return perms

        for role_name in roles_data:
            canonical = normalize_role(role_name, default=role_name) or role_name
            resolved[canonical] = get_inherited_permissions(role_name)
            if role_name != canonical:
                resolved[role_name] = resolved[canonical]

        return resolved
    except Exception:
        return {r: set(perms) for r, perms in DEFAULT_ROLE_HIERARCHY.items()}


def get_permissions_for_role(role: str) -> Set[str]:
    """Get all permissions for a given role name."""
    roles = load_roles_config()
    canonical = normalize_role(role, default=None)
    if canonical and canonical in roles:
        return roles[canonical]
    return roles.get(str(role).lower(), set())


def has_permission(user_role: str, permission: str) -> bool:
    """Check whether a user role has the required permission."""
    perms = get_permissions_for_role(user_role)
    return permission in perms or normalize_role(user_role) == RoleEnum.ADMIN.value


def require_permission(user_role: str, permission: str) -> None:
    """Raise ForbiddenException if user lacks the specified permission."""
    if not has_permission(user_role, permission):
        raise ForbiddenException(
            f"Action requires '{permission}' permission, but role '{user_role}' lacks it."
        )


def is_role_at_least(user_role: str, required_role: str) -> bool:
    """Check if user role rank meets or exceeds the required role rank."""
    user_rank = ROLE_RANK.get(normalize_role(user_role, default="") or "", 0)
    req_rank = ROLE_RANK.get(normalize_role(required_role, default="") or "", 999)
    return user_rank >= req_rank


def require_role(user_role: str, required_role: str) -> None:
    """Raise ForbiddenException if user role rank is lower than required."""
    if not is_role_at_least(user_role, required_role):
        raise ForbiddenException(
            f"Role '{user_role}' does not meet the minimum required role '{required_role}'."
        )


def role_can(user_role: str, *allowed_roles: str) -> bool:
    """Return True when the user role is (or outranks) any of ``allowed_roles``."""
    return any(is_role_at_least(user_role, role) for role in allowed_roles)
