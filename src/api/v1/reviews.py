"""
AssureX Claim Engine - Reviews & Manual Adjudication API Router
Provides endpoints for Reviewer Queue browsing, human decision submissions, and override statistics.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database.session import get_db
from src.dependencies import current_user_role, get_current_user, require_reviewer
from src.models.user import User
from src.schemas.review import (
    CommentPayload,
    HumanOverrideStats,
    ReviewDecisionPayload,
    ReviewQueueResponse,
    ReviewResponse,
)
from src.services import claim_service, review_service

router = APIRouter(prefix="/reviews", tags=["Reviews"])


def _authorized_claim(claim_id: int, current_user: User, db: Session):
    """Load a claim the current user is allowed to comment on / inspect."""
    return claim_service.get_claim_by_id(
        db=db,
        claim_id=claim_id,
        user_id=current_user.id,
        role=current_user_role(current_user),
    )


@router.get("/queue", response_model=ReviewQueueResponse)
def get_manual_review_queue(
    status: Optional[str] = Query(None, description="Filter queue by status"),
    min_fraud_score: Optional[float] = Query(None, description="Filter by minimum fraud score"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(require_reviewer),
    db: Session = Depends(get_db),
):
    """Retrieve claims waiting in the manual review queue."""
    items, total = review_service.get_review_queue(
        db=db,
        skip=skip,
        limit=limit,
        status=status,
        min_fraud_score=min_fraud_score,
    )
    return {"total": total, "items": items}


@router.post("/{claim_id}/comments")
def add_review_comment(
    claim_id: int,
    payload: CommentPayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a note or comment to a claim review audit trail."""
    claim = _authorized_claim(claim_id, current_user, db)
    comment_text = (payload.comment or payload.text or "Note added.").strip()
    if not comment_text:
        raise HTTPException(status_code=422, detail="Comment text cannot be empty.")
    return review_service.add_review_comment(
        db=db,
        claim_id=claim.id,
        reviewer_id=current_user.id,
        comment=comment_text,
    )


@router.get("/{claim_id}")
def get_review_detail(
    claim_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve review and audit details for a specific claim."""
    claim = _authorized_claim(claim_id, current_user, db)
    return review_service.get_review_detail(db=db, claim_id=claim.id)


@router.post("/{claim_id}/decision", response_model=ReviewResponse)
@router.post("/{claim_id}/decide", response_model=ReviewResponse)
@router.post("/{claim_id}/override", response_model=ReviewResponse)
def submit_review_decision(
    claim_id: int,
    payload: ReviewDecisionPayload,
    current_user: User = Depends(require_reviewer),
    db: Session = Depends(get_db),
):
    """Submit reviewer manual decision (APPROVE, REJECT, ESCALATE) or manual override."""
    _authorized_claim(claim_id, current_user, db)
    reasoning_text = payload.reasoning or payload.justification or "Manual adjudication decision recorded"
    return review_service.submit_review_decision(
        db=db,
        claim_id=claim_id,
        reviewer_id=current_user.id,
        decision=payload.decision,
        reasoning=reasoning_text,
        notes=payload.notes,
    )


@router.get("/stats/overrides", response_model=HumanOverrideStats)
def get_override_statistics(
    current_user: User = Depends(require_reviewer),
    db: Session = Depends(get_db),
):
    """Retrieve statistics comparing human reviewer overrides versus original AI model predictions."""
    return review_service.get_human_override_stats(db)
