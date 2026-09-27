"""
AssureX Claim Engine - Cryptographic Hashing Utilities
"""

import hashlib
from pathlib import Path
from typing import BinaryIO, Union


def hash_bytes(data: bytes) -> str:
    """Compute SHA-256 hexadecimal digest of raw bytes."""
    return hashlib.sha256(data).hexdigest()


def hash_string(text: str, encoding: str = "utf-8") -> str:
    """Compute SHA-256 hexadecimal digest of a string."""
    return hashlib.sha256(text.encode(encoding)).hexdigest()


def hash_file(file_path: Union[str, Path], chunk_size: int = 65536) -> str:
    """
    Compute SHA-256 hexadecimal digest of a file on disk.
    Reads in chunks to handle large files memory-efficiently.
    """
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"File not found for hashing: {file_path}")

    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()


def hash_stream(stream: BinaryIO, chunk_size: int = 65536) -> str:
    """
    Compute SHA-256 hexadecimal digest from an open binary file-like stream.
    Preserves stream position if seekable.
    """
    pos = stream.tell() if hasattr(stream, "tell") else None
    hasher = hashlib.sha256()
    try:
        while chunk := stream.read(chunk_size):
            hasher.update(chunk)
    finally:
        if pos is not None and hasattr(stream, "seek"):
            stream.seek(pos)
    return hasher.hexdigest()