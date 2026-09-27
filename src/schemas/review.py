"""
AssureX Claim Engine - Manual Review & Audit Pydantic Schemas
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from src.schemas.user import UserResponse
from src.schemas.warranty import WarrantyResponse


class ReviewBase(BaseModel):
    decision: str = Field(..., max_length=50) # APPROVE, REJECT, REQUEST_INFO, ESCALATE
    reasoning: str = Field(..., min_length=5)
    notes: Optional[str] = None


class ReviewCreate(ReviewBase):
    claim_id: int


class ReviewDecisionPayload(BaseModel):
    decision: str = Field(..., max_length=50) # APPROVE, REJECT, ESCALATE
    reasoning: Optional[str] = None
    justification: Optional[str] = None
    notes: Optional[str] = None


class CommentPayload(BaseModel):
    comment: Optional[str] = None
    text: Optional[str] = None


class ReviewResponse(BaseModel):
    model_config = {'protected_namespaces': (), 'from_attributes': True}
    id: int
    claim_id: int
    reviewer_id: Optional[int] = None
    previous_status: str
    new_status: str
    decision: str
    reasoning: str
    notes: Optional[str] = None
    reviewed_at: datetime
    reviewer: Optional[UserResponse] = None


class ReviewQueueItem(BaseModel):
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
    ai_confidence: Optional[float] = None
    fraud_score: Optional[float] = None
    model_agreement_score: Optional[float] = 1.0
    submitted_at: Optional[Any] = None
    user: Optional[UserResponse] = None
    warranty: Optional[WarrantyResponse] = None


class ReviewQueueResponse(BaseModel):
    total: int
    items: List[ReviewQueueItem]


class HumanOverrideStats(BaseModel):
    total_reviewed: int
    approved_count: int
    rejected_count: int
    escalated_count: int
    override_count: int
    override_rate: float
    agreement_rate: float
    reviewer_breakdown: Dict[str, Any] = {}

