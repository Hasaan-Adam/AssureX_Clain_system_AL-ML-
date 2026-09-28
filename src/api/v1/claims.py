"""
AssureX Claim Engine - Claims Adjudication API Router
Handles claim registration, status queries, detail inspections, status transitions, and customer appeals.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database.session import get_db
from src.dependencies import current_user_role, get_current_user, require_reviewer
from src.models.user import User
from src.schemas.claim import (
    ClaimAppealRequest,
    ClaimCreate,
    ClaimDetailResponse,
    ClaimListResponse,
    ClaimResponse,
    ClaimStatusUpdate,
    ClaimUpdate,
)
from src.services import claim_service
from src.utils.constants import RoleEnum, normalize_role

router = APIRouter(prefix="/claims", tags=["Claims"])

ON_BEHALF_ROLES = (RoleEnum.SERVICE_STAFF, RoleEnum.REVIEWER, RoleEnum.ADMIN)


@router.post("", response_model=ClaimResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=ClaimResponse, status_code=status.HTTP_201_CREATED)
def submit_claim(
    claim_data: ClaimCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Submit a new claim and trigger automated AI & rule-based adjudication.

    Service-centre staff / reviewers / admins may file a claim *on behalf of* a
    customer by passing `customer_id` (or a `warranty_id` owned by that customer).
    The filing agent is stored on the claim for the audit trail.
    """
    role = current_user_role(current_user)
    target_user_id = current_user.id

    if claim_data.customer_id and claim_data.customer_id != current_user.id:
        if role not in {r.value for r in ON_BEHALF_ROLES}:
            raise HTTPException(
                status_code=403,
                detail="Only service-centre staff can file a claim on behalf of another customer.",
            )
        from src.models.user import User as UserModel

        customer = db.query(UserModel).filter(UserModel.id == claim_data.customer_id).first()
        if not customer or not customer.is_active:
            raise HTTPException(status_code=404, detail="Customer account not found.")
        if customer.id == current_user.id:
            raise HTTPException(status_code=400, detail="A claim cannot be filed for your own account via customer_id.")
        target_user_id = customer.id
    elif claim_data.warranty_id and role in {r.value for r in ON_BEHALF_ROLES}:
        from src.models.warranty import Warranty

        warranty = db.query(Warranty).filter(Warranty.id == claim_data.warranty_id).first()
        if warranty and warranty.user_id and warranty.user_id != current_user.id:
            target_user_id = warranty.user_id

    return claim_service.create_claim(
        db=db,
        user_id=target_user_id,
        claim_data=claim_data,
        user_role=role,
        auto_adjudicate=True,
        created_by=current_user.id,
    )


@router.get("", response_model=ClaimListResponse)
@router.get("/", response_model=ClaimListResponse)
def list_claims(
    status: Optional[str] = Query(None, description="Filter by claim status"),
    warranty_id: Optional[int] = Query(None, description="Filter by warranty ID"),
    fault_type: Optional[str] = Query(None, description="Filter by fault type"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level (low/medium/high)"),
    min_confidence: Optional[float] = Query(None, ge=0.0, le=1.0),
    max_confidence: Optional[float] = Query(None, ge=0.0, le=1.0),
    filed_by: Optional[int] = Query(None, description="Filter by the agent who filed the claim"),
    on_behalf: Optional[bool] = Query(None, description="Filter claims filed on behalf of a customer"),
    date_from: Optional[str] = Query(None, description="Submission date from (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Submission date to (YYYY-MM-DD)"),
    search: Optional[str] = Query(None, description="Search by claim number, fault type, or description"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List claims. Customers see only their own claims; service staff, reviewers
    and admins see all claims. Supports the SRS xlii search/filter criteria.
    """
    from src.utils.constants import PRIVILEGED_ROLES

    role = current_user_role(current_user)
    user_id = None if role in PRIVILEGED_ROLES else current_user.id

    claims, total = claim_service.list_claims(
        db=db,
        user_id=user_id,
        status=status,
        warranty_id=warranty_id,
        fault_type=fault_type,
        risk_level=risk_level,
        min_confidence=min_confidence,
        max_confidence=max_confidence,
        filed_by=filed_by,
        on_behalf=on_behalf,
        date_from=date_from,
        date_to=date_to,
        search=search,
        skip=skip,
        limit=limit,
    )
    return {"total": total, "claims": claims}


@router.get("/by-number/{claim_number}", response_model=ClaimDetailResponse)
def get_claim_by_number(
    claim_number: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve a claim by its human-readable claim number (e.g. CLM-20260927-01234)."""
    from database.models import Claim
    from src.utils.constants import PRIVILEGED_ROLES

    claim = db.query(Claim).filter(Claim.claim_id == claim_number).first()
    if not claim:
        raise HTTPException(status_code=404, detail=f"Claim '{claim_number}' was not found.")
    if current_user_role(current_user) not in PRIVILEGED_ROLES and claim.claimant_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only open your own claims.")
    return claim


@router.get("/{claim_id}", response_model=ClaimDetailResponse)
def get_claim(
    claim_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve full claim details, including documents, predictions, and manual reviews."""
    return claim_service.get_claim_by_id(
        db=db,
        claim_id=claim_id,
        user_id=current_user.id,
        role=current_user_role(current_user),
    )


@router.put("/{claim_id}", response_model=ClaimResponse)
def update_claim(
    claim_id: int,
    payload: ClaimUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update the mutable details of an open claim."""
    return claim_service.update_claim(
        db=db,
        claim_id=claim_id,
        update_data=payload,
        user_id=current_user.id,
        role=current_user_role(current_user),
    )


@router.delete("/{claim_id}")
def delete_claim(
    claim_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a draft claim (owner) or any claim (service staff / reviewer / admin)."""
    return claim_service.delete_claim(
        db=db,
        claim_id=claim_id,
        user_id=current_user.id,
        role=current_user_role(current_user),
    )


@router.get("/{claim_id}/timeline")
def get_claim_timeline(
    claim_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """SRS xxxviii: real status-progression timeline for a claim."""
    claim = claim_service.get_claim_by_id(
        db=db,
        claim_id=claim_id,
        user_id=current_user.id,
        role=current_user_role(current_user),
    )
    return claim_service.get_claim_timeline(db, claim)


@router.get("/{claim_id}/audit-logs")
def get_claim_audit_logs(
    claim_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """SRS xlvii: audit trail recorded for a specific claim."""
    from src.utils.constants import PRIVILEGED_ROLES

    role = current_user_role(current_user)
    claim = claim_service.get_claim_by_id(db=db, claim_id=claim_id, user_id=current_user.id, role=role)
    items, total = claim_service.get_claim_audit_logs(db, claim, skip=skip, limit=limit)
    return {
        "claim_number": claim.claim_id,
        "total": total,
        "logs": [
            {
                "id": log.id,
                "action": log.action,
                "actor_id": log.user_id,
                "entity_type": log.entity_type,
                "old_values": log.old_values,
                "new_values": log.new_values,
                "ip_address": log.ip_address,
                "created_at": log.created_at,
            }
            for log in items
        ],
    }


@router.put("/{claim_id}/status", response_model=ClaimResponse)
def update_claim_status(
    claim_id: int,
    payload: ClaimStatusUpdate,
    current_user: User = Depends(require_reviewer),
    db: Session = Depends(get_db),
):
    """Reviewer/Admin endpoint to transition claim status."""
    return claim_service.transition_claim_status(
        db=db,
        claim_id=claim_id,
        new_status=payload.status,
        user_id=current_user.id,
        reason=payload.reason,
        notes=payload.notes,
    )


@router.post("/{claim_id}/appeal", response_model=ClaimResponse)
def appeal_claim_decision(
    claim_id: int,
    payload: ClaimAppealRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Customer endpoint to appeal a rejected claim."""
    return claim_service.appeal_claim(
        db=db,
        claim_id=claim_id,
        user_id=current_user.id,
        appeal_notes=payload.appeal_notes,
    )
