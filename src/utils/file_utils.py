"""
AssureX Claim Engine - File & Upload Security Utilities
"""

import os
import re
import uuid
from pathlib import Path
from typing import Optional, Set, Tuple

ALLOWED_EXTENSIONS: Set[str] = {".pdf", ".png", ".jpg", ".jpeg", ".webp"}
ALLOWED_MIME_TYPES: Set[str] = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/pjpeg",
    "image/webp",
}
MAX_FILE_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB

SAFE_FILENAME_PATTERN = re.compile(r"[^a-zA-Z0-9_.-]")


def sanitize_filename(filename: str) -> str:
    """
    Sanitize an uploaded file's base name:
    - Removes directory path components
    - Replaces unsafe characters with underscores
    - Preserves valid extension
    """
    base = os.path.basename(filename).strip()
    name, ext = os.path.splitext(base)
    clean_name = SAFE_FILENAME_PATTERN.sub("_", name)
    clean_ext = ext.lower()
    if not clean_name:
        clean_name = "document"
    return f"{clean_name}{clean_ext}"


def generate_unique_filename(original_filename: str, prefix: Optional[str] = None) -> str:
    """
    Generate a UUID-based collision-resistant filename while preserving extension.
    Example: 'invoice.pdf' -> 'inv_a1b2c3d4e5f6..._invoice.pdf'
    """
    clean = sanitize_filename(original_filename)
    unique_id = uuid.uuid4().hex[:12]
    pref = f"{prefix}_" if prefix else ""
    return f"{pref}{unique_id}_{clean}"


def validate_file_extension(filename: str, allowed_exts: Optional[Set[str]] = None) -> Tuple[bool, str]:
    """
    Check if a file extension is in the allowed whitelist.
    Returns (is_valid, extension).
    """
    allowed = allowed_exts or ALLOWED_EXTENSIONS
    ext = os.path.splitext(filename)[1].lower()
    if not ext:
        return False, ""
    return (ext in allowed), ext


def validate_mime_type(content_type: str, allowed_mimes: Optional[Set[str]] = None) -> bool:
    """Check if MIME type is in the allowed whitelist."""
    if not content_type:
        return False
    allowed = allowed_mimes or ALLOWED_MIME_TYPES
    return content_type.lower().split(";")[0].strip() in allowed


def validate_file_size(size_bytes: int, max_bytes: int = MAX_FILE_SIZE_BYTES) -> bool:
    """Check if file size does not exceed maximum allowable limit."""
    return 0 < size_bytes <= max_bytes


def ensure_upload_dir(upload_path: str) -> Path:
    """Ensure upload target directory exists and return Path object."""
    path = Path(upload_path).resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path