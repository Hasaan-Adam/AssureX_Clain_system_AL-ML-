"""
AssureX Claim Engine - Warranty Pydantic Schemas
"""

from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field, model_validator

from src.schemas.product import ProductResponse


class WarrantyBase(BaseModel):
    product_id: int
    serial_number: str = Field(..., min_length=1, max_length=100)
    purchase_date: date
    purchase_price: float = Field(0.0, ge=0.0)
    invoice_number: Optional[str] = Field(None, max_length=100)
    store_name: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None
    image_url: Optional[str] = None
    start_date: Optional[date] = None
    expiry_date: Optional[date] = None
    provider: Optional[str] = None
    coverage_conditions: Optional[str] = None
    exclusions: Optional[str] = None
    service_centers: Optional[str] = None


class WarrantyCreate(WarrantyBase):
    pass


class WarrantyUpdate(BaseModel):
    status: Optional[str] = Field(None, max_length=50)
    expiry_date: Optional[date] = None
    notes: Optional[str] = None
    store_name: Optional[str] = None
    image_url: Optional[str] = None


class WarrantyResponse(BaseModel):
    id: int
    warranty_number: str = ""
    user_id: Optional[int] = None
    product_id: int
    serial_number: Optional[str] = ""
    start_date: Optional[date] = None
    purchase_date: Optional[date] = None
    expiry_date: Optional[date] = None
    status: str = "ACTIVE"
    provider: Optional[str] = None
    coverage_conditions: Optional[str] = None
    exclusions: Optional[str] = None
    service_centers: Optional[str] = None
    purchase_price: Optional[float] = 0.0
    invoice_number: Optional[str] = None
    store_name: Optional[str] = None
    notes: Optional[str] = None
    image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    product: Optional[ProductResponse] = None

    model_config = {'from_attributes': True}

    @model_validator(mode="after")
    def apply_effective_status(self) -> "WarrantyResponse":
        """A warranty is EXPIRED once its coverage end date has passed."""
        if self.status and self.status.upper() != "VOIDED" and self.expiry_date:
            if self.expiry_date < date.today():
                self.status = "EXPIRED"
        return self


class WarrantyListResponse(BaseModel):
    total: int
    warranties: List[WarrantyResponse]


class WarrantyExpiryCheckResponse(BaseModel):
    total_checked: int
    alerts_generated: int
    details: List[dict] = []