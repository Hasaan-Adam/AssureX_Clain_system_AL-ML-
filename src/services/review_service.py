"""Review Service - Review Queue and Adjudication Operations"""

from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime

from database.models import Claim, Review, User, Product
from src.core.exceptions import NotFoundError


def get_review_queue(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    min_fraud_score: Optional[float] = None,
    search: Optional[str] = None,
    risk_level: Optional[str] = None,
    priority: Optional[str] = None,
):
    """List claims requiring manual review with filtering."""
    query = db.query(Claim)
    
    if status:
        if status.lower() in ("pending", "all_pending"):
            query = query.filter(
                Claim.status.in_(
                    ["submitted", "under_review", "under_evaluation", "manual_review", "info_required", "escalated"]
                )
            )
        elif status.lower() == "completed":
            query = query.filter(Claim.status.in_(["approved", "rejected", "auto_approved", "closed"]))
        elif status.lower() != "all":
            query = query.filter(Claim.status.ilike(f"%{status}%"))
            
    if search:
        search_pat = f"%{search}%"
        query = query.filter(
            or_(
                Claim.claim_id.ilike(search_pat),
                Claim.fault_type.ilike(search_pat),
                Claim.fault_description.ilike(search_pat),
            )
        )
        
    total = query.count()
    items = query.order_by(Claim.created_at.desc()).offset(skip).limit(limit).all()
    return items, total


list_review_queue = get_review_queue


def submit_review_decision(
    db: Session,
    claim_id: int,
    reviewer_id: int,
    decision: str,
    reasoning: Optional[str] = None,
    notes: Optional[str] = None,
    comments: Optional[str] = None,
    **kwargs: Any,
) -> Review:
    """Submit reviewer decision (approve, reject, escalate, request_info) with instant in-app alerts and email."""
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise NotFoundError("Claim", claim_id)
    
    d = (decision or "").strip().lower()
    norm_decision = "approve"
    if "appr" in d:
        norm_decision = "approve"
    elif "rej" in d:
        norm_decision = "reject"
    elif "esc" in d:
        norm_decision = "escalate"
    elif "info" in d or "req" in d:
        norm_decision = "request_info"
    else:
        norm_decision = d
    
    final_reason = reasoning or kwargs.get("justification") or comments or notes or "Manual review decision recorded"
    final_notes = notes or comments or ""

    review = Review(
        claim_id=claim_id,
        reviewer_id=reviewer_id,
        decision=norm_decision.upper(),
        comments=final_notes,
        override_reason=final_reason,
    )
    db.add(review)
    
    if norm_decision == "approve":
        claim.status = "approved"
        claim.final_decision = "Approved by Reviewer"
    elif norm_decision == "reject":
        claim.status = "rejected"
        claim.final_decision = "Rejected by Reviewer"
    elif norm_decision == "escalate":
        claim.status = "escalated"
        claim.final_decision = "Escalated to Supervisor"
    else:
        claim.status = "info_required"
        claim.final_decision = "Additional Information Required"
    
    claim.decided_at = datetime.utcnow()
    claim.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(review)
    db.refresh(claim)

    # Dispatch In-App Notification & Email to Claimant
    try:
        from src.services.notification_service import create_notification
        from src.services.email_service import send_claim_decision_email

        user = db.query(User).filter(User.id == claim.claimant_id).first()
        prod = db.query(Product).filter(Product.id == claim.product_id).first()
        prod_name = prod.name if prod else "Product"

        create_notification(
            db=db,
            user_id=claim.claimant_id,
            title=f"Claim #{claim.claim_id}: {norm_decision.replace('_', ' ').title()}",
            message=f"Reviewer outcome: {claim.final_decision}. {final_notes or final_reason}".strip(),
            type="claim_status",
            related_entity_type="claim",
            related_entity_id=str(claim.id),
        )

        if user and user.email:
            send_claim_decision_email(
                claim_number=claim.claim_id,
                user_email=user.email,
                user_name=user.full_name or "Customer",
                decision=norm_decision,
                product_name=prod_name,
                comments=final_notes or final_reason,
            )
    except Exception:
        pass

    return review


def get_human_override_stats(db: Session) -> Dict[str, Any]:
    """Get statistics on human reviewer overrides vs AI predictions."""
    total = db.query(Review).count()
    approved = db.query(Review).filter(Review.decision.ilike("%APPROV%")).count()
    rejected = db.query(Review).filter(Review.decision.ilike("%REJECT%")).count()
    escalated = db.query(Review).filter(Review.decision.ilike("%ESCALAT%")).count()
    overrides = db.query(Review).filter(Review.override_reason.isnot(None), Review.override_reason != "").count()
    
    override_rate = round(overrides / total, 4) if total > 0 else 0.0
    agreement_rate = round(1.0 - override_rate, 4) if total > 0 else 1.0

    return {
        "total_reviewed": total,
        "approved_count": approved,
        "rejected_count": rejected,
        "escalated_count": escalated,
        "override_count": overrides,
        "override_rate": override_rate,
        "agreement_rate": agreement_rate,
        "reviewer_breakdown": {},
    }


def add_review_comment(
    db: Session,
    claim_id: int,
    reviewer_id: int,
    comment: str,
) -> Dict[str, Any]:
    """Add a note or comment on a claim review with in-app notification."""
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise NotFoundError("Claim", claim_id)
    
    clean_text = (comment or "").strip() or "Note attached to claim review."
    review = Review(
        claim_id=claim_id,
        reviewer_id=reviewer_id,
        decision="NOTE",
        comments=clean_text,
        override_reason=clean_text,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    user = db.query(User).filter(User.id == reviewer_id).first()

    # In-App notification to claimant if comment was from staff
    try:
        if claim.claimant_id != reviewer_id:
            from src.services.notification_service import create_notification
            create_notification(
                db=db,
                user_id=claim.claimant_id,
                title=f"Reviewer Comment on Claim #{claim.claim_id}",
                message=f"An adjudicator commented: \"{clean_text}\"",
                type="claim_status",
                related_entity_type="claim",
                related_entity_id=str(claim.id),
            )
    except Exception:
        pass

    return {
        "id": review.id,
        "claim_id": claim_id,
        "author_name": user.full_name if user else "Adjudicator",
        "comment": clean_text,
        "text": clean_text,
        "created_at": review.created_at.isoformat() if review.created_at else datetime.utcnow().isoformat(),
    }


def get_review_detail(db: Session, claim_id: int) -> Dict[str, Any]:
    """Get review information for a claim."""
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise NotFoundError("Claim", claim_id)
    reviews = db.query(Review).filter(Review.claim_id == claim_id).order_by(Review.created_at.asc()).all()
    return {
        "claim_id": claim.id,
        "status": claim.status,
        "final_decision": claim.final_decision,
        "reviews": [
            {
                "id": r.id,
                "reviewer_id": r.reviewer_id,
                "author_name": r.reviewer.full_name if r.reviewer else "Adjudicator",
                "decision": r.decision,
                "comments": r.comments,
                "created_at": r.created_at.isoformat() if r.created_at else "",
            }
            for r in reviews
        ]
    }