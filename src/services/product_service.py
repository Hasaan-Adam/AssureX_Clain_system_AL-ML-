"""Product Service - Product Management"""

from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from database.models import Product, WarrantyType
from src.core.exceptions import NotFoundError


def create_product(db: Session, product_data: Dict[str, Any], user_id: int) -> Product:
    """Create a new product with all SRS-required fields and auto-assigned unique Product ID."""
    import time
    ts = int(time.time() * 1000)
    serial_prefix = product_data.get("serial_prefix") or "SN"

    serial_number = (
        product_data.get("serial_number")
        or f"{serial_prefix}-{ts}"
    )

    purchase_date_raw = product_data.get("purchase_date")
    if purchase_date_raw:
        try:
            from datetime import datetime as dt
            purchase_date = dt.strptime(str(purchase_date_raw), "%Y-%m-%d").date()
        except Exception:
            purchase_date = datetime.utcnow().date()
    else:
        purchase_date = datetime.utcnow().date()

    warranty_months = int(product_data.get("warranty_months") or product_data.get("warranty_duration_months") or 12)
    from datetime import timedelta
    warranty_expiry = purchase_date + timedelta(days=warranty_months * 30)

    product = Product(
        product_id=f"PRD-{ts}",
        owner_id=user_id,
        name=product_data.get("model_name") or product_data.get("name") or "Product Model",
        category=product_data.get("category") or "ELECTRONICS",
        brand=product_data.get("brand") or "Generic",
        model_number=product_data.get("model_number") or product_data.get("model_name") or f"MOD-{ts}",
        serial_number=serial_number,
        purchase_date=purchase_date,
        purchase_price=int(float(product_data.get("purchase_price") or product_data.get("msrp") or 0)),
        retailer=product_data.get("retailer") or "Authorized Dealer",
        warranty_duration_months=warranty_months,
        warranty_type=WarrantyType.STANDARD.value if hasattr(WarrantyType.STANDARD, 'value') else "standard",
        warranty_start_date=purchase_date,
        warranty_expiry_date=warranty_expiry,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
    prod = db.query(Product).filter(Product.id == product_id).first()
    if not prod:
        raise NotFoundError("Product", product_id)
    return prod


def redact_product(product: Product) -> Dict[str, Any]:
    """
    Return the public catalogue view of a product: owner-specific facts
    (serial, purchase paperwork) are removed.
    """
    return {
        "id": product.id,
        "product_id": product.product_id,
        "model_name": product.model_name,
        "category": product.category,
        "brand": product.brand,
        "model_number": product.model_number,
        "msrp": product.msrp,
        "warranty_months": product.warranty_months,
        "description": product.description,
        "image_url": product.image_url,
        "is_active": True,
        "created_at": product.created_at,
        "updated_at": product.updated_at,
    }


def get_product_for_user(
    db: Session,
    product_id: int,
    user_id: int,
    role: Optional[str] = None,
) -> Product:
    """
    Load a product and enforce ownership.
    Customers may only read/edit their own registrations; service staff,
    reviewers and admins may act on any product.
    """
    from src.core.exceptions import AuthorizationError
    from src.utils.constants import PRIVILEGED_ROLES, normalize_role

    product = get_product_by_id(db, product_id)
    if normalize_role(role) in PRIVILEGED_ROLES:
        return product
    if product.owner_id != user_id:
        raise AuthorizationError("You do not have access to this product.")
    return product


def delete_product(db: Session, product_id: int, user_id: int, role: Optional[str] = None) -> Dict[str, Any]:
    """Delete a product registration, enforcing ownership for customers."""
    from src.core.exceptions import AuthorizationError
    from src.utils.constants import PRIVILEGED_ROLES, normalize_role
    from src.services.audit_service import log_action

    product = get_product_by_id(db, product_id)

    if normalize_role(role) not in PRIVILEGED_ROLES and product.owner_id != user_id:
        raise AuthorizationError("You do not have access to this product.")

    claims = getattr(product, "claims", None) or []
    if claims:
        from src.core.exceptions import ValidationError

        raise ValidationError("This product has claims and cannot be deleted.")

    product_id_value = product.product_id
    db.delete(product)
    db.commit()

    log_action(
        db=db,
        action="PRODUCT_DELETE",
        entity_type="Product",
        entity_id=str(product_id),
        user_id=user_id,
        old_values={"product_id": product_id_value},
    )
    return {"deleted": True, "product_id": product_id_value, "message": "Product deleted successfully"}


def list_products(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    category: Optional[str] = None,
    brand: Optional[str] = None,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    owner_id: Optional[int] = None,
):
    query = db.query(Product)
    if category:
        query = query.filter(Product.category.ilike(f"%{category}%"))
    if brand:
        query = query.filter(Product.brand.ilike(f"%{brand}%"))
    if owner_id:
        query = query.filter(Product.owner_id == owner_id)
    if search:
        search_pat = f"%{search}%"
        query = query.filter(
            (Product.name.ilike(search_pat))
            | (Product.brand.ilike(search_pat))
            | (Product.model_number.ilike(search_pat))
            | (Product.serial_number.ilike(search_pat))
        )
    total = query.count()
    products = query.order_by(Product.created_at.desc()).offset(skip).limit(limit).all()
    return products, total


def update_product(db: Session, product_id: int, update_data: Any, user_id: Optional[int] = None) -> Product:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise NotFoundError("Product", product_id)
    
    if hasattr(update_data, 'model_dump'):
        data_dict = update_data.model_dump(exclude_unset=True)
    elif isinstance(update_data, dict):
        data_dict = update_data
    else:
        data_dict = {}

    for key, value in data_dict.items():
        if value is not None and hasattr(product, key):
            setattr(product, key, value)
    product.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(product)
    return product


def get_categories(db: Optional[Session] = None) -> List[str]:
    if db:
        cats = [c[0] for c in db.query(Product.category).distinct().all() if c[0]]
        if cats:
            return sorted(list(set(cats)))
    return ["electronics", "home_appliances", "mobile_phones"]


def get_brands(db: Optional[Session] = None) -> List[str]:
    if db:
        brands = [b[0] for b in db.query(Product.brand).distinct().all() if b[0]]
        if brands:
            return sorted(list(set(brands)))
    return ["Apple", "Dell", "Gree", "Haier", "HP", "LG", "Panasonic", "Samsung", "Sony", "Xiaomi"]