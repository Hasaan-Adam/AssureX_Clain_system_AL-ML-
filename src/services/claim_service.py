"""Claim Service - Claim Management and Adjudication Lifecycle"""

from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, date
import time

from database.models import Claim, User, Product, Warranty
from src.core.exceptions import NotFoundError, ValidationError


def _next_claim_number(db: Session) -> str:
    """Generate a unique, human-readable claim number (FR x)."""
    while True:
        candidate = f"CLM-{datetime.utcnow().strftime('%Y%m%d')}-{int(time.time() * 1000) % 100000:05d}"
        if not db.query(Claim.id).filter(Claim.claim_id == candidate).first():
            return candidate


def create_claim(
    db: Session,
    user_id: int,
    claim_data: Any,
    user_role: Optional[str] = "customer",
    auto_adjudicate: bool = True,
    created_by: Optional[int] = None,
    service_center: Optional[str] = None,
) -> Claim:
    """Create a new claim with automated adjudication, notifications, and email alerts."""
    if hasattr(claim_data, "model_dump"):
        data_dict = claim_data.model_dump()
    elif isinstance(claim_data, dict):
        data_dict = claim_data
    else:
        data_dict = dict(claim_data)

    product_id = data_dict.get("product_id")
    warranty_id = data_dict.get("warranty_id")

    if not product_id and warranty_id:
        warranty = db.query(Warranty).filter(Warranty.id == warranty_id).first()
        if not warranty:
            raise NotFoundError("Warranty", warranty_id)
        product_id = warranty.product_id

    if product_id and not warranty_id:
        warranty = db.query(Warranty).filter(Warranty.product_id == product_id).first()
        warranty_id = warranty.id if warranty else None

    if not product_id:
        raise ValidationError(
            "A product or warranty reference is required to submit a claim."
        )

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise NotFoundError("Product", product_id)

    ts = int(time.time() * 1000) % 100000

    f_date = data_dict.get("fault_occurrence_date") or data_dict.get("incident_date") or datetime.utcnow().date()
    if isinstance(f_date, str):
        try:
            f_date = datetime.strptime(f_date, "%Y-%m-%d").date()
        except Exception:
            f_date = datetime.utcnow().date()

    requested_amount = data_dict.get("claim_amount")
    claim_amount = float(requested_amount) if requested_amount else float(product.purchase_price or 0.0)

    filed_by = created_by or user_id
    claim = Claim(
        claim_id=_next_claim_number(db),
        claimant_id=user_id,
        product_id=product_id,
        warranty_id=warranty_id,
        fault_occurrence_date=f_date,
        fault_type=data_dict.get("fault_type") or "General Hardware Defect",
        fault_description=data_dict.get("description") or data_dict.get("fault_description") or "Fault description",
        damage_type=data_dict.get("damage_type") or "component_failure",
        claim_amount=claim_amount,
        claim_submission_date=datetime.utcnow().date(),
        submitted_at=datetime.utcnow(),
        processed_at=datetime.utcnow(),
        status="submitted",
        created_by=filed_by,
        filing_channel="service_center" if filed_by != user_id else "self_service",
        service_center=service_center,
    )
    db.add(claim)
    db.commit()
    db.refresh(claim)

    from src.services.audit_service import log_action

    log_action(
        db=db,
        action="CLAIM_SUBMIT",
        entity_type="Claim",
        entity_id=str(claim.id),
        user_id=filed_by,
        new_values={
            "claim_number": claim.claim_id,
            "claimant_id": user_id,
            "on_behalf": claim.is_filed_on_behalf,
            "filing_channel": claim.filing_channel,
            "claim_amount": claim.claim_amount,
        },
    )

    if auto_adjudicate:
        try:
            from src.services.prediction_service import adjudicate_claim
            adjudicate_claim(db, claim.id, data_dict)
            db.refresh(claim)
        except Exception:
            claim.status = "under_review"
            claim.final_decision = "Manual Review Required"
            db.commit()
            db.refresh(claim)

    try:
        from src.services.notification_service import create_notification, notify_all_reviewers
        create_notification(
            db=db,
            user_id=user_id,
            title=f"Claim #{claim.claim_id} Submitted",
            message=f"Your claim for {product.name} ({claim.fault_type}) was submitted and is under automated review.",
            type="claim_status",
            related_entity_type="claim",
            related_entity_id=str(claim.id),
        )
        
        notify_all_reviewers(
            db=db,
            title=f"New Claim: {claim.claim_id}",
            message=f"New claim for {product.name} ({product.category}) submitted by user #{user_id}.",
            related_entity_type="claim",
            related_entity_id=str(claim.id),
        )
    except Exception:
        pass

    try:
        from src.services.email_service import send_claim_submission_email
        user = db.query(User).filter(User.id == user_id).first()
        if user and user.email:
            send_claim_submission_email(
                claim_number=claim.claim_id,
                user_email=user.email,
                user_name=user.full_name or "Customer",
                product_name=product.name,
                fault_type=claim.fault_type,
            )
    except Exception:
        pass

    return claim


def get_claim_by_id(
    db: Session,
    claim_id: int,
    user_id: Optional[int] = None,
    is_admin_or_reviewer: bool = False,
    role: Optional[str] = None,
) -> Optional[Claim]:
    """
    Get claim by ID with authorization checks.

    Privileged roles (service staff, reviewers, admins) may open any claim;
    everybody else only their own claims.
    """
    from src.utils.constants import PRIVILEGED_ROLES, normalize_role

    if is_admin_or_reviewer or (role and normalize_role(role) in PRIVILEGED_ROLES):
        is_admin_or_reviewer = True

    query = db.query(Claim).filter(Claim.id == claim_id)
    if user_id is not None and not is_admin_or_reviewer:
        query = query.filter(Claim.claimant_id == user_id)
    claim = query.first()
    if not claim:
        raise NotFoundError("Claim", claim_id)
    return claim


def list_claims(
    db: Session,
    user_id: Optional[int] = None,
    claimant_id: Optional[int] = None,
    status: Optional[str] = None,
    warranty_id: Optional[int] = None,
    fault_type: Optional[str] = None,
    risk_level: Optional[str] = None,
    min_confidence: Optional[float] = None,
    max_confidence: Optional[float] = None,
    filed_by: Optional[int] = None,
    on_behalf: Optional[bool] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
):
    """List claims with filters (SRS xlii) and return (claims, total)."""
    from src.utils.dates import parse_date

    query = db.query(Claim)

    uid = user_id or claimant_id
    if uid is not None:
        query = query.filter(Claim.claimant_id == uid)

    if status:
        query = query.filter(Claim.status.ilike(f"%{status}%"))

    if warranty_id:
        query = query.filter(Claim.warranty_id == warranty_id)

    if fault_type:
        query = query.filter(Claim.fault_type.ilike(f"%{fault_type}%"))

    if filed_by:
        query = query.filter(Claim.created_by == filed_by)

    if on_behalf is not None:
        if on_behalf:
            query = query.filter(Claim.created_by.isnot(None), Claim.created_by != Claim.claimant_id)
        else:
            query = query.filter(
                (Claim.created_by.is_(None)) | (Claim.created_by == Claim.claimant_id)
            )

    for raw, operator in ((date_from, "ge"), (date_to, "le")):
        if raw:
            parsed = parse_date(raw)
            if parsed:
                column = Claim.claim_submission_date
                query = query.filter(column >= parsed) if operator == "ge" else query.filter(column <= parsed)

    if risk_level or min_confidence is not None or max_confidence is not None:
        candidates = query.all()
        wanted_risk = (risk_level or "").strip().lower()
        filtered = []
        for claim in candidates:
            confidence = claim.ai_confidence
            if min_confidence is not None and (confidence is None or confidence < min_confidence):
                continue
            if max_confidence is not None and (confidence is None or confidence > max_confidence):
                continue
            if wanted_risk:
                score = claim.fraud_score or 0.0
                level = "high" if score >= 0.7 else ("medium" if score >= 0.4 else "low")
                if level != wanted_risk:
                    continue
            filtered.append(claim)
        total = len(filtered)
        items = filtered[skip: skip + limit]
        return items, total

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Claim.claim_id.ilike(search_pattern))
            | (Claim.fault_type.ilike(search_pattern))
            | (Claim.fault_description.ilike(search_pattern))
        )
        
    total = query.count()
    items = query.order_by(Claim.created_at.desc()).offset(skip).limit(limit).all()
    return items, total


def transition_claim_status(
    db: Session,
    claim_id: int,
    new_status: str,
    user_id: Optional[int] = None,
    reason: Optional[str] = None,
    notes: Optional[str] = None,
) -> Claim:
    """Transition claim to new status with customer notification & email."""
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise NotFoundError("Claim", claim_id)
    
    old_status = claim.status
    claim.status = new_status
    claim.updated_at = datetime.utcnow()
    target = (new_status or "").lower()
    if target in ("approved", "auto_approved"):
        claim.final_decision = "APPROVE"
        claim.decided_at = datetime.utcnow()
    elif target == "rejected":
        claim.final_decision = "REJECT"
        claim.decided_at = datetime.utcnow()
        claim.rejection_reason = reason or notes
    elif target in ("under_review", "manual_review", "escalated", "submitted"):
        claim.final_decision = "MANUAL_REVIEW"
    elif target == "closed":
        claim.final_decision = claim.final_decision or "APPROVE"
        claim.resolved_at = datetime.utcnow()
    if target in ("approved", "rejected", "auto_approved", "closed", "settled"):
        claim.resolved_at = claim.resolved_at or datetime.utcnow()
    db.commit()
    db.refresh(claim)

    try:
        from src.services.notification_service import create_notification
        from src.services.email_service import send_claim_decision_email
        
        user = db.query(User).filter(User.id == claim.claimant_id).first()
        prod = db.query(Product).filter(Product.id == claim.product_id).first()
        prod_name = prod.name if prod else "Product"

        create_notification(
            db=db,
            user_id=claim.claimant_id,
            title=f"Claim #{claim.claim_id} Status: {new_status.replace('_', ' ').title()}",
            message=f"Status changed from '{old_status}' to '{new_status}'. {reason or notes or ''}".strip(),
            type="claim_status",
            related_entity_type="claim",
            related_entity_id=str(claim.id),
        )

        if user and user.email:
            send_claim_decision_email(
                claim_number=claim.claim_id,
                user_email=user.email,
                user_name=user.full_name or "Customer",
                decision=new_status,
                product_name=prod_name,
                comments=reason or notes,
            )
    except Exception:
        pass

    return claim


def appeal_claim(db: Session, claim_id: int, user_id: int, appeal_notes: Optional[str] = None) -> Claim:
    """Appeal a rejected claim (SRS: appeal request re-enters the review queue)."""
    claim = db.query(Claim).filter(Claim.id == claim_id, Claim.claimant_id == user_id).first()
    if not claim:
        raise NotFoundError("Claim", claim_id)
    if claim.status not in ("rejected", "closed", "appeal_requested"):
        raise ValidationError("Only a rejected or closed claim can be appealed.")
    claim.status = "appeal_requested"
    claim.appeal_notes = appeal_notes
    claim.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(claim)

    try:
        from src.services.notification_service import notify_all_reviewers
        notify_all_reviewers(
            db=db,
            title=f"Appeal Filed: {claim.claim_id}",
            message=f"Customer filed an appeal on claim #{claim.claim_id}. Notes: {appeal_notes or 'None'}",
            related_entity_type="claim",
            related_entity_id=str(claim.id),
        )
    except Exception:
        pass

    return claim


def update_claim(
    db: Session,
    claim_id: int,
    update_data: Any,
    user_id: Optional[int] = None,
    role: Optional[str] = None,
) -> Claim:
    """Update mutable claim details while the claim is still open."""
    claim = get_claim_by_id(db=db, claim_id=claim_id, user_id=user_id, role=role)
    if claim.status in ("approved", "rejected", "closed"):
        raise ValidationError("A closed or decided claim can no longer be edited.")

    if hasattr(update_data, "model_dump"):
        data = update_data.model_dump(exclude_unset=True)
    else:
        data = dict(update_data or {})

    field_map = {
        "description": "fault_description",
        "claim_amount": "claim_amount",
    }
    for key, value in data.items():
        if value is None:
            continue
        if key in field_map:
            setattr(claim, field_map[key], value)
        elif hasattr(claim, key):
            setattr(claim, key, value)

    claim.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(claim)

    from src.services.audit_service import log_action

    log_action(
        db=db,
        action="CLAIM_UPDATE",
        entity_type="Claim",
        entity_id=str(claim.id),
        user_id=user_id,
        new_values={k: str(v) for k, v in data.items() if v is not None},
    )
    return claim


def delete_claim(db: Session, claim_id: int, user_id: Optional[int] = None, role: Optional[str] = None) -> Dict[str, Any]:
    """Delete a draft claim (owner) or any claim (privileged roles)."""
    claim = get_claim_by_id(db=db, claim_id=claim_id, user_id=user_id, role=role)
    from src.utils.constants import PRIVILEGED_ROLES, normalize_role

    is_privileged = normalize_role(role) in PRIVILEGED_ROLES
    if not is_privileged and claim.status != "draft":
        raise ValidationError("Only draft claims can be deleted by their owner.")

    claim_number = claim.claim_id
    for doc in list(claim.documents):
        db.delete(doc)
    for prediction in list(claim.predictions):
        db.delete(prediction)
    db.delete(claim)
    db.commit()

    from src.services.audit_service import log_action

    log_action(
        db=db,
        action="CLAIM_DELETE",
        entity_type="Claim",
        entity_id=str(claim_id),
        user_id=user_id,
        new_values={"claim_number": claim_number},
    )
    return {"deleted": True, "claim_number": claim_number, "message": f"Claim {claim_number} deleted."}


CLAIM_STATUS_FLOW = [
    ("draft", "Draft"),
    ("submitted", "Submitted"),
    ("under_review", "AI Adjudication & OCR"),
    ("info_required", "Additional Information Required"),
    ("manual_review", "Human Review"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
    ("closed", "Closed"),
]


def get_claim_timeline(db: Session, claim: Claim) -> Dict[str, Any]:
    """
    Build the real status timeline for a claim from its recorded events
    (SRS xxxviii) instead of inferring stages from the current status.
    """
    events: List[Dict[str, Any]] = []

    def add(stage: str, label: str, at: Optional[datetime], note: str = "", actor: Optional[str] = None):
        events.append(
            {
                "stage": stage,
                "label": label,
                "occurred_at": at.isoformat() if at else None,
                "note": note,
                "actor_id": actor,
            }
        )

    add("draft", "Draft", claim.created_at, "Claim record created")
    if claim.submitted_at:
        who = "Service centre" if claim.is_filed_on_behalf else "Customer"
        add("submitted", "Submitted", claim.submitted_at, f"Filed via {claim.filing_channel or 'self_service'}", who)
    if claim.processed_at:
        add("under_review", "AI Adjudication & OCR", claim.processed_at, "Automated evaluation started")
    if claim.status == "info_required":
        add("info_required", "Additional Information Required", claim.updated_at, "More evidence requested")

    for review in claim.reviews:
        decision = (getattr(review, "decision", None) or "").upper()
        stage = {
            "APPROVE": "approved",
            "REJECT": "rejected",
            "MANUAL_REVIEW": "manual_review",
            "ESCALATE": "manual_review",
        }.get(decision)
        if stage:
            add(stage, stage.replace("_", " ").title(), review.created_at, getattr(review, "comments", None) or "")

    for prediction in claim.predictions:
        if prediction.final_decision and prediction.model_consistency_status:
            add(
                "manual_review" if "manual" in str(prediction.final_decision).lower() else "under_review",
                "AI adjudication",
                prediction.created_at,
                f"{prediction.final_decision} (model status: {prediction.model_consistency_status})",
            )

    if claim.decided_at:
        stage = "approved" if claim.status in ("approved", "auto_approved") else "rejected"
        add(stage, stage.title(), claim.decided_at, claim.rejection_reason or "")
    if claim.resolved_at:
        add("closed", "Closed", claim.resolved_at, "Claim closed")

    return {
        "claim_id": claim.claim_id,
        "claim_number": claim.claim_id,
        "current_status": claim.status,
        "stages": [{"stage": s, "label": lbl} for s, lbl in CLAIM_STATUS_FLOW],
        "events": events,
    }


def get_claim_audit_logs(db: Session, claim: Claim, skip: int = 0, limit: int = 100):
    """Audit-trail entries recorded against this claim (SRS xlvii)."""
    from database.models import AuditLog

    query = db.query(AuditLog).filter(
        (AuditLog.entity_type == "Claim") & (AuditLog.entity_id == str(claim.id))
    )
    total = query.count()
    items = (
        query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    )
    return items, total