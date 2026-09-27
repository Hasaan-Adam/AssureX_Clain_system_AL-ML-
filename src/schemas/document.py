"""
AssureX Claim Engine - Document Pydantic Schemas
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DocumentBase(BaseModel):
    document_type: str = Field(..., max_length=100)
    file_name: str = Field(..., max_length=255)
    mime_type: str = Field(..., max_length=100)
    file_size: int = Field(..., ge=0)


class DocumentCreate(DocumentBase):
    claim_id: Optional[int] = None
    warranty_id: Optional[int] = None
    file_path: str
    file_hash: str


class DocumentResponse(BaseModel):
    id: int
    claim_id: Optional[int] = None
    warranty_id: Optional[int] = None
    document_type: str
    file_name: str
    file_path: str
    file_size: int
    mime_type: str
    file_hash: str
    ocr_extracted_text: Optional[str] = None
    ocr_confidence: Optional[float] = None
    ocr_metadata: Optional[Dict[str, Any]] = None
    uploaded_at: Optional[datetime] = None

    model_config = {'from_attributes': True}


class DocumentListResponse(BaseModel):
    total: int
    documents: List[DocumentResponse]


class OCRResultResponse(BaseModel):
    document_id: int
    text: str
    confidence: float
    metadata: Dict[str, Any] = {}
    extracted_entities: Dict[str, Any] = {}