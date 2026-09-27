"""
AssureX Claim Engine - Claim Pydantic Schemas
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from src.schemas.document import DocumentResponse
from src.schemas.prediction import PredictionResponse
from src.schemas.review import ReviewResponse
from src.schemas.user import UserResponse
from src.schemas.warranty import WarrantyResponse


class ClaimBase(BaseModel):
    model_config = {'protected_namespaces': ()}
    product_id: Optional[int] = None
    warranty_id: Optional[int] = None
    fault_occurrence_date: Optional[date] = None
    fault_type: str = Field(..., max_length=100)
    fault_description: Optional[str] = None
    damage_type: Optional[str] = None
    description: str = Field(..., min_length=5)
    claim_amount: float = Field(0.0, ge=0.0)
    claim_submission_date: Optional[date] = None


class ClaimCreate(ClaimBase):
    customer_id: Optional[int] = None


class ClaimUpdate(BaseModel):
    fault_type: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, min_length=5)
    claim_amount: Optional[float] = Field(None, ge=0.0)


class ClaimStatusUpdate(BaseModel):
    status: str = Field(..., max_length=50) # draft, submitted, validating, ai_analyzed, under_review, approved, rejected, escalated, settled, closed
    reason: Optional[str] = None
    notes: Optional[str] = None


class ClaimAppealRequest(BaseModel):
    appeal_notes: str = Field(..., min_length=10)


class ClaimResponse(BaseModel):
    model_config = {'protected_namespaces': (), 'from_attributes': True}
    id: int
    claim_number: str
    user_id: int
    warranty_id: int
    fault_type: str
    description: str
    claim_amount: float
    status: str
    ai_decision: Optional[str] = None
    final_decision: Optional[str] = None
    fraud_score: Optional[float] = 0.0
    ai_confidence: Optional[float] = 0.0
    model_agreement_score: Optional[float] = 1.0
    rejection_reason: Optional[str] = None
    escalation_reason: Optional[str] = None
    appeal_notes: Optional[str] = None
    submitted_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class ClaimDetailResponse(ClaimResponse):
    user: Optional[UserResponse] = None
    warranty: Optional[WarrantyResponse] = None
    documents: List[DocumentResponse] = []
    predictions: List[PredictionResponse] = []
    reviews: List[ReviewResponse] = []

    model_config = {'protected_namespaces': (), 'from_attributes': True}


class ClaimListResponse(BaseModel):
    total: int
    claims: List[ClaimResponse]
