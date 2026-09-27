"""
AssureX Claim Engine - Warranties API Router
Handles customer warranty registration, verification, detail queries, and expiry alert triggers.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database.session import get_db
from src.dependencies import current_user_role, get_current_user, require_role
from src.models.user import User
from src.schemas.warranty import (
    WarrantyCreate,
    WarrantyExpiryCheckResponse,
    WarrantyListResponse,
    WarrantyResponse,
    WarrantyUpdate,
)
from src.services import warranty_service
from src.utils.constants import RoleEnum

router = APIRouter(prefix="/warranties", tags=["Warranties"])

#: Roles allowed to administer any customer's warranty record.
WARRANTY_ADMIN_ROLES = (RoleEnum.SERVICE_STAFF, RoleEnum.REVIEWER, RoleEnum.ADMIN)


class SerialVerifyRequest(BaseModel):
    serial_number: str = Field(..., min_length=1, max_length=100)
    product_id: Optional[int] = None


@router.post("", response_model=WarrantyResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=WarrantyResponse, status_code=status.HTTP_201_CREATED)
def register_warranty(
    warranty_data: WarrantyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Register a new product warranty for the current customer."""
    return warranty_service.create_warranty(
        db=db,
        user_id=current_user.id,
        warranty_data=warranty_data.model_dump(),
    )


@router.get("", response_model=WarrantyListResponse)
@router.get("/", response_model=WarrantyListResponse)
def list_warranties(
    status: Optional[str] = Query(None, description="Filter by status (ACTIVE, EXPIRED, VOIDED)"),
    search: Optional[str] = Query(None, description="Search by warranty number, serial, or store"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List warranties. Customers see only their own warranties; Staff/Admins see all warranties.
    """
    role = current_user_role(current_user)
    user_id = current_user.id if role == RoleEnum.CUSTOMER.value else None
    warranties, total = warranty_service.list_warranties(
        db=db,
        user_id=user_id,
        status=status,
        search=search,
        skip=skip,
        limit=limit,
    )
    return {"total": total, "warranties": warranties}


@router.get("/expiring", response_model=WarrantyListResponse)
def list_expiring_warranties(
    days: int = Query(30, ge=1, le=365, description="Days before expiry to include"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Warranties that expire within the next `days` days (FR viii/ix - active,
    expired, nearing expiration and extended coverage in one view).
    """
    role = current_user_role(current_user)
    user_id = current_user.id if role == RoleEnum.CUSTOMER.value else None
    warranties, total = warranty_service.list_expiring_warranties(
        db=db,
        user_id=user_id,
        days=days,
    )
    return {"total": total, "warranties": warranties}


@router.post("/verify-serial")
def verify_serial_number_post(
    payload: SerialVerifyRequest,
    db: Session = Depends(get_db),
):
    """Verify a serial number against registered warranties (POST variant)."""
    return _verify_serial(db, payload.serial_number.strip())


@router.get("/verify/{serial_number}")
def verify_serial_number(
    serial_number: str,
    db: Session = Depends(get_db),
):
    """
    Public warranty verification by serial number.

    Only non-identifying warranty facts are returned (existence, warranty
    number, status, coverage window) - never the owner's identity.
    """
    return _verify_serial(db, serial_number)


def _verify_serial(db: Session, serial_number: str) -> dict:
    if not serial_number or not serial_number.strip():
        raise HTTPException(status_code=400, detail="Serial number is required")

    warranty = warranty_service.get_warranty_by_serial(db, serial_number)
    if not warranty:
        return {
            "exists": False,
            "status": "NOT_FOUND",
            "message": "No warranty registered for this serial.",
        }

    return {
        "exists": True,
        "warranty_id": warranty.id,
        "warranty_number": warranty.warranty_number,
        "status": warranty.effective_status,
        "start_date": str(warranty.start_date) if warranty.start_date else None,
        "expiry_date": str(warranty.expiry_date) if warranty.expiry_date else None,
        "product": warranty.product.name if warranty.product else None,
        "brand": warranty.product.brand if warranty.product else None,
        "serial_number": warranty.serial_number,
    }


@router.get("/{warranty_id}", response_model=WarrantyResponse)
def get_warranty(
    warranty_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve warranty details."""
    is_admin = current_user_role(current_user) in {r.value for r in WARRANTY_ADMIN_ROLES}
    return warranty_service.get_warranty_by_id(
        db=db,
        warranty_id=warranty_id,
        user_id=current_user.id if not is_admin else None,
        is_admin=is_admin,
    )


@router.put("/{warranty_id}", response_model=WarrantyResponse)
def update_warranty(
    warranty_id: int,
    update_data: WarrantyUpdate,
    current_user: User = Depends(require_role(*WARRANTY_ADMIN_ROLES)),
    db: Session = Depends(get_db),
):
    """Service staff / reviewer / admin update warranty status or details."""
    return warranty_service.update_warranty(
        db=db,
        warranty_id=warranty_id,
        update_data=update_data.model_dump(exclude_unset=True),
        admin_user_id=current_user.id,
    )


@router.delete("/{warranty_id}")
def delete_warranty(
    warranty_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete/void a warranty record. The product owner may remove a warranty that
    has not been used in a claim; service staff and admins may remove any.
    """
    return warranty_service.delete_warranty(
        db=db,
        warranty_id=warranty_id,
        user_id=current_user.id,
        role=current_user_role(current_user),
    )


@router.post("/check-expiry", response_model=WarrantyExpiryCheckResponse)
def trigger_expiry_alert_check(
    current_user: User = Depends(require_role(RoleEnum.ADMIN)),
    db: Session = Depends(get_db),
):
    """Admin cron trigger to check warranty expiration dates and issue alert notifications."""
    result = warranty_service.generate_expiry_alerts(db)
    return result

