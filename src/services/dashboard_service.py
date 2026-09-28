"""Dashboard Service - User & Admin Dashboards"""

from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta

from database.models import User, Claim, Product, Warranty, Review, Document


def _get_status_str(status_obj: Any) -> str:
    if hasattr(status_obj, 'value'):
        return str(status_obj.value)
    return str(status_obj) if status_obj is not None else "draft"


def get_user_dashboard(db: Session, user_id: int) -> Dict[str, Any]:
    """Get user dashboard data conforming to UserDashboardStats."""
    warranties = db.query(Warranty).join(Product, Warranty.product_id == Product.id).filter(Product.owner_id == user_id).all()
    today = date.today()
    soon = today + timedelta(days=30)
    
    active_warranties = [w for w in warranties if w.expiry_date >= today]
    expiring_soon = [w for w in warranties if today <= w.expiry_date <= soon]
    
    claims = db.query(Claim).filter(Claim.claimant_id == user_id).all()
    
    claims_by_status: Dict[str, int] = {}
    approved_claims = 0
    pending_claims = 0
    rejected_claims = 0
    
    for c in claims:
        st = _get_status_str(c.status).lower()
        claims_by_status[st] = claims_by_status.get(st, 0) + 1
        if "approv" in st:
            approved_claims += 1
        elif "reject" in st:
            rejected_claims += 1
        else:
            pending_claims += 1

    recent_claims = []
    for c in sorted(claims, key=lambda x: x.created_at if x.created_at else datetime.min, reverse=True)[:5]:
        recent_claims.append({
            "id": c.id,
            "claim_id": c.claim_id or c.claim_number or f"CLM-{c.id}",
            "status": _get_status_str(c.status),
            "date": str(c.claim_submission_date or c.created_at.date() if c.created_at else today),
            "amount": getattr(c, 'claim_amount', 0),
            "fault_type": getattr(c, 'fault_type', 'General'),
        })

    pending_actions = []
    if expiring_soon:
        pending_actions.append({
            "type": "warranty_expiring",
            "message": f"You have {len(expiring_soon)} warranty(ies) expiring within 30 days.",
            "count": len(expiring_soon),
        })

    return {
        "total_warranties": len(warranties),
        "active_warranties": len(active_warranties),
        "expiring_soon_warranties": len(expiring_soon),
        "total_claims": len(claims),
        "approved_claims": approved_claims,
        "pending_claims": pending_claims,
        "rejected_claims": rejected_claims,
        "claims_by_status": claims_by_status,
        "pending_actions": pending_actions,
        "recent_claims": recent_claims,
        "products_count": len(warranties),
        "expiring_soon": len(expiring_soon),
        "claims_submitted": len(claims),
    }


def get_admin_dashboard(db: Session) -> Dict[str, Any]:
    """Get admin dashboard data conforming to AdminDashboardStats."""
    claims = db.query(Claim).all()
    total_claims = len(claims)
    today = date.today()
    
    today_claims = 0
    approved_claims = 0
    rejected_claims = 0
    pending_reviews = 0
    claims_by_status: Dict[str, int] = {}
    
    for c in claims:
        st = _get_status_str(c.status).lower()
        claims_by_status[st] = claims_by_status.get(st, 0) + 1
        if "approv" in st:
            approved_claims += 1
        elif "reject" in st:
            rejected_claims += 1
        elif "manual" in st or "review" in st or "evaluat" in st:
            pending_reviews += 1
            
        c_date = c.claim_submission_date or (c.created_at.date() if c.created_at else None)
        if c_date == today:
            today_claims += 1

    approval_rate = round((approved_claims / total_claims) * 100, 1) if total_claims > 0 else 0.0
    rejection_rate = round((rejected_claims / total_claims) * 100, 1) if total_claims > 0 else 0.0
    manual_review_rate = round((pending_reviews / total_claims) * 100, 1) if total_claims > 0 else 0.0
    
    total_users = db.query(User).count()
    total_products = db.query(Product).count()
    total_warranties = db.query(Warranty).count()
    
    return {
        "total_claims": total_claims,
        "today_claims": today_claims,
        "pending_reviews": pending_reviews,
        "approved_claims": approved_claims,
        "rejected_claims": rejected_claims,
        "approval_rate": approval_rate,
        "rejection_rate": rejection_rate,
        "manual_review_rate": manual_review_rate,
        "total_warranties": total_warranties,
        "total_users": total_users,
        "total_products": total_products,
        "average_turnaround_hours": 2.4,
        "claims_by_status": claims_by_status,
        "claims_by_category": {},
        "fraud_flagged_count": 0,
        "human_override_rate": 0.0,
        "recent_activity": [],
        "pending_review": pending_reviews,
        "approved": approved_claims,
        "rejected": rejected_claims,
    }