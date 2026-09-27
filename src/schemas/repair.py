from datetime import date
from typing import Optional
from pydantic import BaseModel, Field

class RepairCreate(BaseModel):
    product_id: int
    claim_id: Optional[int] = None
    repair_date: date
    repair_center: str = Field(..., max_length=100)
    parts_replaced: Optional[str] = None
    repair_cost: float = Field(..., ge=0.0)
    authorized_status: str = Field("yes", max_length=10)

class RepairResponse(RepairCreate):
    id: int
    
    class Config:
        from_attributes = True
