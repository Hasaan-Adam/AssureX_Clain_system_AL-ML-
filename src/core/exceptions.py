"""
AssureX Claim Engine - Custom Exception Hierarchy

Provides structured, user-friendly error responses without exposing internal details.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import HTTPException
from fastapi.responses import JSONResponse


class AssureXBaseException(Exception):
    """Base exception for all AssureX custom exceptions."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class AuthenticationError(AssureXBaseException):
    """Invalid credentials, expired token, or missing authentication."""

    def __init__(self, message: str = "Authentication required.", details: Optional[Dict[str, Any]] = None):
        super().__init__("AUTHENTICATION_FAILED", message, 401, details)


class AuthorizationError(AssureXBaseException):
    """Authenticated user lacks required role or permission."""

    def __init__(self, message: str = "Insufficient permissions.", details: Optional[Dict[str, Any]] = None):
        super().__init__("AUTHORIZATION_FAILED", message, 403, details)


class ValidationError(AssureXBaseException):
    """Business logic validation failure (e.g., invalid dates, missing documents)."""

    def __init__(self, message: str = "Validation failed.", details: Optional[Dict[str, Any]] = None):
        super().__init__("VALIDATION_ERROR", message, 422, details)


class NotFoundError(AssureXBaseException):
    """Requested resource does not exist."""

    def __init__(self, resource: str, identifier: Any, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            "NOT_FOUND",
            f"{resource} with identifier '{identifier}' not found.",
            404,
            {**(details or {}), "resource": resource, "identifier": str(identifier)},
        )


class ConflictError(AssureXBaseException):
    """Resource conflict (e.g., duplicate claim, serial mismatch)."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__("CONFLICT", message, 409, details)


class RateLimitError(AssureXBaseException):
    """Too many requests from client."""

    def __init__(self, message: str = "Rate limit exceeded. Please try again later.", details: Optional[Dict[str, Any]] = None):
        super().__init__("RATE_LIMIT_EXCEEDED", message, 429, details)


class InternalError(AssureXBaseException):
    """Unexpected server error (wrapped from raw exceptions)."""

    def __init__(self, message: str = "Internal server error.", details: Optional[Dict[str, Any]] = None):
        super().__init__("INTERNAL_ERROR", message, 500, details)


class ModelNotLoadedError(AssureXBaseException):
    """Required ML model artifact not found or failed to load."""

    def __init__(self, model_name: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            "MODEL_NOT_LOADED",
            f"ML model '{model_name}' is not loaded. Please train or deploy the model first.",
            503,
            {**(details or {}), "model_name": model_name},
        )


class FileProcessingError(AssureXBaseException):
    """File upload, OCR, or image processing failure."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__("FILE_PROCESSING_ERROR", message, 400, details)


class PolicyViolationError(AssureXBaseException):
    """Claim violates warranty policy rules (hard-fail conditions)."""

    def __init__(self, violations: List[str], details: Optional[Dict[str, Any]] = None):
        super().__init__(
            "POLICY_VIOLATION",
            "Claim violates one or more warranty policy rules.",
            422,
            {**(details or {}), "violations": violations},
        )


def format_error_response(
    status_code: int,
    code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
) -> JSONResponse:
    """Standardized JSON error envelope for all API responses."""
    content = {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
            "timestamp": __import__("datetime").datetime.utcnow().isoformat() + "Z",
        }
    }
    return JSONResponse(status_code=status_code, content=content)


ForbiddenException = AuthorizationError
ConflictException = ConflictError
EntityNotFoundException = NotFoundError
PolicyViolationException = PolicyViolationError
RateLimitException = RateLimitError
ServiceUnavailableException = ModelNotLoadedError
UnauthorizedException = AuthenticationError
ValidationException = ValidationError


def raise_if(condition: bool, exception: AssureXBaseException) -> None:
    """Raise exception if condition is True, else no-op."""
    if condition:
        raise exception