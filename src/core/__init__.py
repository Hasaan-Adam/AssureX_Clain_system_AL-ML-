"""
AssureX Claim Engine - Core Security, Permissions, Exceptions, and Logging
"""

from src.core.exceptions import (
    AssureXBaseException,
    ConflictError,
    NotFoundError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    InternalError,
    ModelNotLoadedError,
    FileProcessingError,
    PolicyViolationError,
    RateLimitError,
    format_error_response,
    raise_if,
)
from src.core.logging_config import get_logger, setup_logging
from src.core.permissions import (
    get_permissions_for_role,
    has_permission,
    is_role_at_least,
    load_roles_config,
    require_permission,
    require_role,
)
from src.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)

__all__ = [
    "AssureXBaseException",
    "ConflictError",
    "NotFoundError",
    "ValidationError",
    "AuthenticationError",
    "AuthorizationError",
    "InternalError",
    "ModelNotLoadedError",
    "FileProcessingError",
    "PolicyViolationError",
    "RateLimitError",
    "format_error_response",
    "raise_if",
    "setup_logging",
    "get_logger",
    "load_roles_config",
    "get_permissions_for_role",
    "has_permission",
    "require_permission",
    "is_role_at_least",
    "require_role",
    "verify_password",
    "get_password_hash",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
]