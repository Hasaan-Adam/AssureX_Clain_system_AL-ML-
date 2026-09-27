"""
AssureX Claim Engine - Product Pydantic Schemas
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    model_config = {'protected_namespaces': ()}
    model_name: str = Field(..., min_length=1, max_length=255)
    category: str = Field(..., min_length=1, max_length=100) # ELECTRONICS, HOME_APPLIANCES, MOBILE_PHONES
    brand: str = Field(..., min_length=1, max_length=100)
    serial_prefix: Optional[str] = Field(None, max_length=50)
    model_number: Optional[str] = Field(None, max_length=100)
    serial_number: Optional[str] = Field(None, max_length=100)
    purchase_date: Optional[str] = None
    purchase_price: Optional[float] = Field(None, ge=0.0)
    retailer: Optional[str] = Field(None, max_length=255)
    msrp: float = Field(0.0, ge=0.0)
    warranty_months: int = Field(12, ge=1, le=120)
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    model_config = {'protected_namespaces': ()}
    model_name: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    brand: Optional[str] = Field(None, min_length=1, max_length=100)
    serial_prefix: Optional[str] = Field(None, max_length=50)
    msrp: Optional[float] = Field(None, ge=0.0)
    warranty_months: Optional[int] = Field(None, ge=1, le=120)
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    model_config = {'protected_namespaces': (), 'from_attributes': True}
    id: int
    product_id: Optional[str] = None
    model_name: str
    category: str
    brand: str
    serial_prefix: Optional[str] = None
    model_number: Optional[str] = None
    serial_number: Optional[str] = None
    purchase_date: Optional[datetime] = None
    purchase_price: Optional[float] = None
    retailer: Optional[str] = None
    msrp: float
    warranty_months: int
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ProductListResponse(BaseModel):
    total: int
    products: List[ProductResponse]
