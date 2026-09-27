"""Document Service - Document Management, Access Control & OCR persistence"""

from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import hashlib
import logging
import os
from pathlib import Path

from database.models import Document, DocumentType, Claim
from src.core.exceptions import ForbiddenException, NotFoundError, ValidationError
from src.utils.constants import PRIVILEGED_ROLES, normalize_role
from src.utils.file_utils import (
    ALLOWED_EXTENSIONS,
    MAX_FILE_SIZE_BYTES,
    ensure_upload_dir,
    sanitize_filename,
    validate_file_extension,
    validate_file_size,
    validate_mime_type,
)

logger = logging.getLogger(__name__)

UPLOAD_DIR = "uploads"

VALID_DOCUMENT_TYPES = {t.value for t in DocumentType}


def _resolve_claim_id(db: Session, claim_id: Optional[int], warranty_id: Optional[int]) -> Optional[int]:
    """Return the claim a document belongs to (direct claim, or via warranty)."""
    if claim_id:
        return claim_id
    if warranty_id:
        claim = (
            db.query(Claim)
            .filter(Claim.warranty_id == warranty_id)
            .order_by(Claim.created_at.desc())
            .first()
        )
        return claim.id if claim else None
    return None


def store_document(
    db: Session,
    file_bytes: Optional[bytes] = None,
    file_name: Optional[str] = None,
    mime_type: Optional[str] = None,
    document_type: str = "other",
    claim_id: Optional[int] = None,
    warranty_id: Optional[int] = None,
    user_id: Optional[int] = None,
    uploader_id: Optional[int] = None,
    document_data: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> Document:
    """
    Store a document on disk and in the database.

    Filenames are sanitised, and the extension / MIME type / file size are
    validated against the upload allow-list before anything touches the disk.
    """
    data = document_data or {}
    uid = user_id or uploader_id or data.get("uploader_id")
    if not uid:
        raise ValidationError("An uploader is required to store a document.")

    c_id = _resolve_claim_id(db, claim_id, warranty_id)
    dtype = (document_type or data.get("document_type") or DocumentType.OTHER.value)
    if hasattr(dtype, "value"):
        dtype = dtype.value
    dtype = str(dtype).lower().strip()
    if dtype not in VALID_DOCUMENT_TYPES:
        raise ValidationError(
            f"Unsupported document type '{dtype}'. Allowed values: {sorted(VALID_DOCUMENT_TYPES)}"
        )

    mtype = mime_type or data.get("mime_type") or "image/jpeg"
    fname = sanitize_filename(file_name or data.get("file_name") or "document.jpg")

    if file_bytes is not None:
        is_valid_ext, ext = validate_file_extension(fname)
        if not is_valid_ext:
            raise ValidationError(
                f"File type '{ext or fname}' is not allowed. Upload one of: {sorted(ALLOWED_EXTENSIONS)}"
            )
        if not validate_mime_type(mtype):
            raise ValidationError(f"Content type '{mtype}' is not allowed for document uploads.")
        if not validate_file_size(len(file_bytes)):
            raise ValidationError(
                f"File is empty or exceeds the {MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB upload limit."
            )

    upload_dir = ensure_upload_dir(UPLOAD_DIR)
    safe_name = f"doc_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}_{fname}"
    file_path = str(upload_dir / safe_name)

    file_hash = ""
    file_size = 0

    if file_bytes:
        file_size = len(file_bytes)
        file_hash = hashlib.sha256(file_bytes).hexdigest()
        with open(file_path, "wb") as f:
            f.write(file_bytes)
    elif data.get("file_path") and os.path.exists(data.get("file_path")):
        file_path = data.get("file_path")
        with open(file_path, "rb") as f:
            content = f.read()
        file_hash = hashlib.sha256(content).hexdigest()
        file_size = len(content)
    else:
        raise ValidationError("No readable file content was supplied.")

    doc = Document(
        claim_id=c_id,
        uploader_id=uid,
        document_type=dtype,
        file_path=file_path,
        file_hash=file_hash,
        file_size=file_size,
        mime_type=mtype,
        extracted_data=data.get("extracted_data"),
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    from src.services.audit_service import log_action

    log_action(
        db=db,
        action="DOCUMENT_UPLOAD",
        entity_type="Document",
        entity_id=str(doc.id),
        user_id=uid,
        new_values={
            "document_type": dtype,
            "claim_id": c_id,
            "file_hash": file_hash,
            "file_size": file_size,
        },
    )
    return doc


def has_document_access(db: Session, doc: Document, user_id: Optional[int], user_role: Optional[str]) -> bool:
    """Ownership rule: uploader, claim owner, or a privileged role."""
    role = normalize_role(user_role, default="customer")
    if role in PRIVILEGED_ROLES:
        return True
    if doc.uploader_id and user_id and doc.uploader_id == user_id:
        return True
    claim = doc.claim
    if claim and user_id and claim.claimant_id == user_id:
        return True
    if claim and claim.warranty and user_id and claim.warranty.user_id == user_id:
        return True
    return False


def get_document_by_id(
    db: Session,
    doc_id: Optional[int] = None,
    document_id: Optional[int] = None,
    user_id: Optional[int] = None,
    user_role: Optional[str] = None,
    enforce_access: bool = True,
    **kwargs: Any,
) -> Document:
    """Fetch a document, enforcing the caller's access rights."""
    target_id = doc_id or document_id
    doc = db.query(Document).filter(Document.id == target_id).first()
    if not doc:
        raise NotFoundError("Document", target_id or 0)

    if enforce_access and not has_document_access(db, doc, user_id, user_role):
        raise ForbiddenException("You do not have access to this document.")
    return doc


def list_documents_for_claim(db: Session, claim_id: int) -> List[Document]:
    return db.query(Document).filter(Document.claim_id == claim_id).all()


def list_documents_for_warranty(db: Session, warranty_id: int) -> List[Document]:
    claim_ids = db.query(Claim.id).filter(Claim.warranty_id == warranty_id).subquery()
    return db.query(Document).filter(Document.claim_id.in_(claim_ids)).all()


def check_access_rights(db: Session, doc_id: int, user_id: int, user_role: str) -> bool:
    doc = get_document_by_id(db, doc_id, enforce_access=False)
    return has_document_access(db, doc, user_id, user_role)


def check_document_hash_exists(db: Session, file_hash: str) -> bool:
    return db.query(Document).filter(Document.file_hash == file_hash).first() is not None


def find_duplicate_documents(db: Session, file_hash: str, exclude_id: Optional[int] = None) -> List[Document]:
    """Documents already using the same file hash (SRS xxxi)."""
    query = db.query(Document).filter(Document.file_hash == file_hash)
    if exclude_id:
        query = query.filter(Document.id != exclude_id)
    return query.all()


def perform_ocr_on_image(image_path: str) -> Dict[str, Any]:
    """Run the real OCR engine on a stored file and return its result."""
    from src.services.ocr_service import perform_ocr_on_image as _run_ocr

    path = Path(image_path)
    if not path.exists():
        raise NotFoundError("Document file", str(image_path))
    with open(path, "rb") as f:
        return _run_ocr(f.read())


def process_document_ocr(db: Session, doc_id: int) -> Document:
    """Run OCR for a stored document and persist the real result."""
    doc = get_document_by_id(db, doc_id, enforce_access=False)
    if not doc:
        raise NotFoundError("Document", doc_id)

    ocr_result = perform_ocr_on_image(doc.file_path)

    entities: Dict[str, Any] = {}
    if ocr_result.get("text"):
        from src.services.extraction_service import extract_entities_from_text

        entities = extract_entities_from_text(ocr_result["text"])

    doc.apply_ocr_result(
        text=ocr_result.get("text", ""),
        confidence=ocr_result.get("confidence", 0.0),
        metadata=ocr_result.get("metadata", {}),
        entities=entities,
    )
    db.commit()
    db.refresh(doc)
    return doc


def verify_extracted_data(
    db: Session,
    doc: Document,
    verified_data: Optional[Dict[str, Any]],
    user_id: int,
) -> Document:
    """Persist user/reviewer corrections to OCR output and mark it verified."""
    payload = doc.ocr_payload
    if verified_data:
        entities = dict(payload.get("entities") or {})
        entities.update(verified_data)
        payload["entities"] = entities
        payload["text"] = payload.get("text", "")
        payload["confidence"] = payload.get("confidence", 0.0)
        payload["metadata"] = dict(payload.get("metadata") or {})
        payload["metadata"]["corrected_by_user"] = True
        doc.extracted_data = __import__("json").dumps(payload, default=str)

    doc.is_verified = True
    doc.verified_by = user_id
    doc.verified_at = datetime.utcnow()
    db.commit()
    db.refresh(doc)

    from src.services.audit_service import log_action

    log_action(
        db=db,
        action="DOCUMENT_VERIFY",
        entity_type="Document",
        entity_id=str(doc.id),
        user_id=user_id,
        new_values={"corrected_fields": sorted((verified_data or {}).keys())},
    )
    return doc


def delete_document(db: Session, doc: Document, user_id: int) -> Dict[str, Any]:
    """Delete a document record and its file from disk."""
    file_path = doc.file_path
    db.delete(doc)
    db.commit()

    if file_path:
        try:
            p = Path(file_path)
            if p.exists() and p.is_file():
                p.unlink()
        except OSError as exc:  # pragma: no cover - best effort cleanup
            logger.warning("Could not remove file %s: %s", file_path, exc)

    from src.services.audit_service import log_action

    log_action(
        db=db,
        action="DOCUMENT_DELETE",
        entity_type="Document",
        entity_id=str(doc.id),
        user_id=user_id,
    )
    return {"message": "Document deleted successfully", "document_id": doc.id}
