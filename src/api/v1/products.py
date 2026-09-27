"""
AssureX Claim Engine - Products Catalog API Router
Handles product registration, updates, browsing, category listings, and brand queries.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from database.session import get_db
from src.dependencies import current_user_role, get_current_user, get_optional_user, require_staff
from src.models.user import User
from src.schemas.product import (
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
)
from src.services import product_service
from src.utils.constants import PRIVILEGED_ROLES

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=ProductListResponse)
@router.get("/", response_model=ProductListResponse)
def list_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    search: Optional[str] = Query(None, description="Search by model name, brand, or serial"),
    is_active: Optional[bool] = Query(None, description="Filter active/inactive products"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    """
    Browse the product catalogue.

    Catalogue browsing is public (no personal data is exposed), but signed-in
    customers only ever see their own registered devices, while service staff,
    reviewers and admins see the full catalogue.
    """
    role = current_user_role(current_user) if current_user else None
    owner_filter = None
    if current_user is not None:
        owner_filter = None if role in PRIVILEGED_ROLES else current_user.id
    else:
        # Anonymous browsing: public catalogue entries only (no owner records).
        owner_filter = -1

    products, total = product_service.list_products(
        db=db,
        category=category,
        brand=brand,
        search=search,
        is_active=is_active,
        owner_id=owner_filter,
        skip=skip,
        limit=limit,
    )
    return {"total": total, "products": products}


@router.get("/categories", response_model=List[str])
def list_categories(
    db: Session = Depends(get_db),
):
    """Retrieve all distinct product categories."""
    return product_service.get_categories(db)


@router.get("/brands", response_model=List[str])
def list_brands(
    db: Session = Depends(get_db),
):
    """Retrieve all distinct product brands."""
    return product_service.get_brands(db)


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db),
):
    """Register a new catalogue product (service staff / reviewer / admin)."""
    return product_service.create_product(
        db=db,
        product_data=product_data.model_dump(),
        user_id=current_user.id,
    )


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve a product's specifications.

    Public catalogue facts (model, brand, category, warranty length) are always
    visible. Owner-specific facts (serial, purchase date/price, retailer) are
    only returned to the owner or to service staff / reviewers / admins.
    """
    product = product_service.get_product_by_id(db, product_id)

    role = current_user_role(current_user) if current_user else None
    is_owner = current_user is not None and product.owner_id == current_user.id
    if not is_owner and role not in PRIVILEGED_ROLES:
        product = product_service.redact_product(product)
    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    update_data: ProductUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update product specifications (owner or service staff / reviewer / admin)."""
    product_service.get_product_for_user(
        db, product_id, current_user.id, current_user_role(current_user)
    )
    return product_service.update_product(
        db=db,
        product_id=product_id,
        update_data=update_data,
        user_id=current_user.id,
    )


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a product registration (blocked while claims exist)."""
    return product_service.delete_product(
        db,
        product_id,
        current_user.id,
        current_user_role(current_user),
    )
