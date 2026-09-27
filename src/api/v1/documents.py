"""
AssureX Claim Engine - Documents & Evidence API Router
Handles file uploads, download streaming, document metadata, and OCR entity triggers.
"""

from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Body, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from database.session import get_db
from src.dependencies import current_user_role, get_current_user
from src.models.user import User
from src.schemas.document import (
    DocumentListResponse,
    DocumentResponse,
    OCRResultResponse,
)
from src.services import claim_service, document_service, extraction_service, ocr_service

router = APIRouter(prefix="/documents", tags=["Documents"])


def _load_document(db: Session, document_id: int, current_user: User):
    """Fetch a document while enforcing the caller's ownership/role rights."""
    return document_service.get_document_by_id(
        db=db,
        document_id=document_id,
        user_id=current_user.id,
        user_role=current_user_role(current_user),
    )


@router.post("/scan-invoice")
async def scan_invoice_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Directly run AI OCR on an uploaded invoice/receipt image and return extracted structured entities
    (invoice_number, purchase_date, purchase_price, store_name, serial_number, ocr_text, confidence)
    for instant form autofilling.
    """
    file_bytes = await file.read()
    ocr_res = ocr_service.perform_ocr_on_image(file_bytes)
    entities = extraction_service.extract_entities_from_text(ocr_res.get("text", ""))

    return {
        "success": True,
        "ocr_text": ocr_res.get("text", ""),
        "confidence": ocr_res.get("confidence", 0.0),
        "metadata": ocr_res.get("metadata", {}),
        "entities": entities,
        "invoice_number": entities.get("invoice_number"),
        "purchase_date": entities.get("purchase_date"),
        "purchase_price": entities.get("purchase_price"),
        "serial_number": entities.get("serial_number"),
        "store_name": entities.get("retailer"),
    }


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form(...),
    claim_id: Optional[int] = Form(None),
    warranty_id: Optional[int] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upload supporting document or photo evidence with automatic SHA-256 calculation.
    """
    file_bytes = await file.read()
    doc = document_service.store_document(
        db=db,
        file_bytes=file_bytes,
        file_name=file.filename or "uploaded_document",
        mime_type=file.content_type or "application/octet-stream",
        document_type=document_type,
        claim_id=claim_id,
        warranty_id=warranty_id,
        user_id=current_user.id,
    )
    return doc


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document_metadata(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve document metadata by ID."""
    return _load_document(db, document_id, current_user)


@router.get("/{document_id}/download")
def download_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Download the raw document file."""
    doc = _load_document(db, document_id, current_user)
    file_path = Path(doc.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Stored file is no longer available.")

    return FileResponse(
        path=file_path,
        filename=doc.file_name,
        media_type=doc.mime_type,
    )


@router.post("/ocr/{document_id}", response_model=OCRResultResponse)
def run_ocr_extraction(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Run OCR extraction and structured entity parsing on an uploaded document image."""
    doc = _load_document(db, document_id, current_user)
    doc_with_ocr = ocr_service.process_document_ocr(db, doc.id)
    entities = doc_with_ocr.ocr_entities or extraction_service.extract_entities_from_text(
        doc_with_ocr.ocr_extracted_text or ""
    )

    return {
        "document_id": doc_with_ocr.id,
        "text": doc_with_ocr.ocr_extracted_text or "",
        "confidence": doc_with_ocr.ocr_confidence or 0.0,
        "metadata": doc_with_ocr.ocr_metadata or {},
        "extracted_entities": entities,
    }


@router.get("/claim/{claim_id}")
def get_documents_by_claim(
    claim_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve all documents attached to a specific claim (owner or privileged role)."""
    claim = claim_service.get_claim_by_id(
        db=db,
        claim_id=claim_id,
        user_id=current_user.id,
        role=current_user_role(current_user),
    )
    return document_service.list_documents_for_claim(db, claim.id)


@router.get("/duplicates/{document_id}")
def get_duplicate_documents(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """SRS xxxi: other documents that already use the same file hash."""
    doc = _load_document(db, document_id, current_user)
    duplicates = document_service.find_duplicate_documents(db, doc.file_hash, exclude_id=doc.id)
    return {
        "document_id": doc.id,
        "file_hash": doc.file_hash,
        "duplicate_count": len(duplicates),
        "duplicates": [
            {
                "id": d.id,
                "claim_id": d.claim_id,
                "document_type": d.document_type,
                "uploaded_at": d.created_at,
            }
            for d in duplicates
        ],
    }


@router.put("/{document_id}/verify")
def verify_document_data(
    document_id: int,
    verified_data: Optional[dict] = Body(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    SRS Req vii: Allow users and reviewers to verify and correct extracted OCR document values.
    """
    doc = _load_document(db, document_id, current_user)
    doc = document_service.verify_extracted_data(
        db=db,
        doc=doc,
        verified_data=verified_data,
        user_id=current_user.id,
    )
    return {
        "status": "success",
        "message": "Document data verified successfully",
        "document_id": doc.id,
        "is_verified": doc.is_verified,
        "extracted_data": doc.ocr_payload,
        "verified_at": doc.verified_at,
    }


@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a document (owner of the claim, uploader, or privileged role)."""
    doc = _load_document(db, document_id, current_user)
    return document_service.delete_document(db=db, doc=doc, user_id=current_user.id)

