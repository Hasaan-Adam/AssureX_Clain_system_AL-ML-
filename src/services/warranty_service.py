"""Warranty Service - Warranty Management"""

import time
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta

from database.models import Warranty, Product
from src.core.exceptions import ConflictError, NotFoundError, ValidationError

#: Serials are unique per active warranty (SRS duplicate-claim/serial rules).
SERIAL_PREFIX_DEFAULT = "SN"


def _next_warranty_number(db: Session) -> str:
    """Generate a unique warranty number (WRN-YYYYMMDD-#####)."""
    while True:
        candidate = f"WRN-{datetime.utcnow().strftime('%Y%m%d')}-{int(time.time() * 1000) % 100000:05d}"
        if not db.query(Warranty.id).filter(Warranty.warranty_number == candidate).first():
            return candidate


def _to_date(value: Any, field: str) -> Optional[date]:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValidationError(f"{field} must be a valid date in YYYY-MM-DD format.") from exc


def create_warranty(db: Session, warranty_data: Dict[str, Any], user_id: int) -> Warranty:
    """Create a new warranty and associate it with a customer-owned product instance."""
    catalog_product = None
    product_id = warranty_data.get("product_id")
    if product_id:
        catalog_product = db.query(Product).filter(Product.id == product_id).first()

    p_date = _to_date(warranty_data.get("purchase_date"), "purchase_date") or date.today()
    start_d = _to_date(warranty_data.get("start_date"), "start_date") or p_date

    months = 12
    if warranty_data.get("warranty_duration_months"):
        months = int(warranty_data.get("warranty_duration_months"))
    elif catalog_product and catalog_product.warranty_duration_months:
        months = int(catalog_product.warranty_duration_months)

    expiry_d = _to_date(warranty_data.get("expiry_date"), "expiry_date") or (start_d + timedelta(days=months * 30))
    if expiry_d <= p_date:
        raise ValidationError("Warranty expiry date must be after the purchase date.")

    serial = str(warranty_data.get("serial_number") or "").strip()
    if not serial:
        serial = f"{SERIAL_PREFIX_DEFAULT}-{int(time.time() * 1000)}"
    serial = serial.upper()

    # A serial may only be registered once, and only by its current owner.
    existing_product = db.query(Product).filter(Product.serial_number == serial).first()
    if existing_product:
        if existing_product.owner_id != user_id:
            raise ConflictError(
                "This serial number is already registered to another account.",
                details={"serial_number": serial},
            )
        existing_warranty = (
            db.query(Warranty).filter(Warranty.product_id == existing_product.id).first()
        )
        if existing_warranty:
            raise ConflictError(
                f"An active warranty already exists for serial {serial} "
                f"({existing_warranty.warranty_number}).",
                details={"serial_number": serial, "warranty_number": existing_warranty.warranty_number},
            )

    ts = int(time.time() * 1000)
    purchase_price = warranty_data.get("purchase_price")
    if purchase_price is None:
        purchase_price = catalog_product.purchase_price if catalog_product else 0

    product = Product(
        product_id=f"PRD-{ts}",
        owner_id=user_id,
        name=catalog_product.name if catalog_product else (warranty_data.get("product_name") or "Device"),
        category=catalog_product.category if catalog_product else (warranty_data.get("category") or "electronics"),
        brand=catalog_product.brand if catalog_product else (warranty_data.get("brand") or "Generic"),
        model_number=catalog_product.model_number if catalog_product else f"MOD-{ts}",
        serial_number=serial,
        purchase_date=p_date,
        purchase_price=int(purchase_price or 0),
        retailer=warranty_data.get("store_name")
        or warranty_data.get("retailer")
        or (catalog_product.retailer if catalog_product else "Retail Store"),
        warranty_duration_months=months,
        warranty_type="standard",
        warranty_start_date=start_d,
        warranty_expiry_date=expiry_d,
    )
    if warranty_data.get("image_url"):
        product.custom_image_url = warranty_data.get("image_url")
        product.image_url = warranty_data.get("image_url")
    db.add(product)
    db.flush()

    warranty = Warranty(
        warranty_number=_next_warranty_number(db),
        user_id=user_id,
        product_id=product.id,
        serial_number=serial,
        provider=warranty_data.get("provider")
        or (product.brand + " Coverage" if product.brand else "Standard Manufacturer"),
        start_date=start_d,
        purchase_date=p_date,
        expiry_date=expiry_d,
        status="ACTIVE",
        purchase_price=float(purchase_price or 0),
        invoice_number=warranty_data.get("invoice_number"),
        store_name=warranty_data.get("store_name") or warranty_data.get("retailer"),
        notes=warranty_data.get("notes"),
        warranty_duration_months=months,
        coverage_conditions=warranty_data.get("coverage_conditions")
        or "Standard OEM Comprehensive Coverage",
        exclusions=warranty_data.get("exclusions") or "Accidental drop, liquid damage, unauthorized repairs",
        service_centers=warranty_data.get("service_centers") or "Authorized OEM Service Centers",
    )
    if warranty_data.get("image_url"):
        warranty.custom_image_url = warranty_data.get("image_url")
    db.add(warranty)
    db.commit()
    db.refresh(warranty)
    return warranty


def get_warranty_by_id(
    db: Session,
    warranty_id: int,
    user_id: Optional[int] = None,
    is_admin: bool = False,
) -> Optional[Warranty]:
    query = db.query(Warranty).filter(Warranty.id == warranty_id)
    if user_id is not None and not is_admin:
        query = query.filter(Warranty.user_id == user_id)
    warranty = query.first()
    if not warranty:
        raise NotFoundError("Warranty", warranty_id)
    return warranty


def get_warranty_by_serial(db: Session, serial: str) -> Optional[Warranty]:
    serial = (serial or "").strip().upper()
    if not serial:
        return None
    return (
        db.query(Warranty)
        .filter(Warranty.serial_number == serial)
        .order_by(Warranty.expiry_date.desc())
        .first()
    )


def list_warranties(
    db: Session,
    user_id: Optional[int] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    product_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
):
    query = db.query(Warranty)

    if user_id is not None:
        query = query.filter(Warranty.user_id == user_id)
    if product_id is not None:
        query = query.filter(Warranty.product_id == product_id)
        
    today = date.today()
    if status:
        if status.upper() == "EXPIRED":
            query = query.filter(Warranty.expiry_date < today)
        elif status.upper() == "ACTIVE":
            query = query.filter(Warranty.expiry_date >= today)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Warranty.warranty_number.ilike(search_pattern))
            | (Warranty.serial_number.ilike(search_pattern))
            | (Warranty.store_name.ilike(search_pattern))
            | (Warranty.provider.ilike(search_pattern))
        )
        
    total = query.count()
    items = query.order_by(Warranty.created_at.desc()).offset(skip).limit(limit).all()
    return items, total


def list_expiring_warranties(
    db: Session,
    user_id: Optional[int] = None,
    days: int = 30,
):
    """Warranties expiring within the next `days` days (FR viii/ix)."""
    today = date.today()
    threshold = today + timedelta(days=days)
    query = db.query(Warranty)
    if user_id is not None:
        query = query.filter(Warranty.user_id == user_id)
    query = query.filter(
        Warranty.expiry_date >= today,
        Warranty.expiry_date <= threshold,
        Warranty.status != "VOIDED",
    )
    items = query.order_by(Warranty.expiry_date.asc()).all()
    return items, len(items)


def delete_warranty(db: Session, warranty_id: int, user_id: int, role: str = "customer") -> Dict[str, Any]:
    """
    Delete a warranty record.

    Customers may only remove a warranty on their own product, and only while
    the warranty has not been used in a submitted claim. Service staff,
    reviewers and admins may remove any warranty.
    """
    from database.models import Claim
    from src.core.exceptions import ForbiddenException
    from src.utils.constants import PRIVILEGED_ROLES

    warranty = db.query(Warranty).filter(Warranty.id == warranty_id).first()
    if not warranty:
        raise NotFoundError("Warranty", warranty_id)

    is_privileged = role in PRIVILEGED_ROLES
    if not is_privileged:
        owner_id = warranty.user_id or (warranty.product.owner_id if warranty.product else None)
        if owner_id != user_id:
            raise ForbiddenException("You can only remove your own warranty records.")
        linked_claims = db.query(Claim).filter(Claim.warranty_id == warranty_id).count()
        if linked_claims:
            raise ForbiddenException(
                "This warranty is already linked to a submitted claim and cannot be removed."
            )

    warranty_number = warranty.warranty_number
    db.delete(warranty)
    db.commit()
    return {
        "deleted": True,
        "warranty_id": warranty_id,
        "warranty_number": warranty_number,
        "message": f"Warranty {warranty_number} removed.",
    }


def update_warranty(
    db: Session,
    warranty_id: int,
    update_data: Any,
    admin_user_id: Optional[int] = None,
) -> Warranty:
    if hasattr(update_data, 'model_dump'):
        data_dict = update_data.model_dump(exclude_unset=True)
    elif isinstance(update_data, dict):
        data_dict = update_data
    else:
        data_dict = {}

    warranty = db.query(Warranty).filter(Warranty.id == warranty_id).first()
    if not warranty:
        raise NotFoundError("Warranty", warranty_id)
        
    for key, value in data_dict.items():
        if value is not None and hasattr(warranty, key):
            setattr(warranty, key, value)
            
    warranty.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(warranty)
    return warranty


def generate_expiry_alerts(db: Session, days_ahead: int = 30) -> Dict[str, Any]:
    from database.models import Notification
    today = date.today()
    threshold = today + timedelta(days=days_ahead)
    expiring = db.query(Warranty).filter(
        Warranty.expiry_date <= threshold,
        Warranty.expiry_date >= today,
    ).all()
    
    notifications_created = 0
    details = []
    
    for warr in expiring:
        user_id = warr.user_id or (warr.product.owner_id if warr.product else None)
        if not user_id:
            continue
            
        days_left = (warr.expiry_date - today).days
        
        # Check if an alert already exists for this warranty in the last 7 days
        recent_alert = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.related_entity_type == "warranty",
            Notification.related_entity_id == str(warr.id),
            Notification.created_at >= datetime.utcnow() - timedelta(days=7)
        ).first()
        
        if not recent_alert:
            product_name = warr.product.name if warr.product else "your product"
            notif = Notification(
                user_id=user_id,
                title="Warranty Expiring Soon",
                message=f"Your warranty for {product_name} will expire in {days_left} days ({warr.expiry_date}).",
                type="WARRANTY_EXPIRY",
                related_entity_type="warranty",
                related_entity_id=str(warr.id)
            )
            db.add(notif)
            notifications_created += 1
            details.append(
                {
                    "warranty_id": warr.id,
                    "warranty_number": warr.warranty_number,
                    "serial_number": warr.serial_number,
                    "days_left": days_left,
                    "user_id": user_id,
                }
            )

    if notifications_created > 0:
        db.commit()
        
    return {
        "total_checked": len(expiring),
        "alerts_generated": notifications_created,
        "details": details
    }