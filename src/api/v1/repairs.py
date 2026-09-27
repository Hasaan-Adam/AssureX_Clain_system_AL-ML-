from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database.session import get_db
from src.dependencies import require_role
from src.schemas.repair import RepairCreate, RepairResponse
from database.models import RepairHistory

router = APIRouter(prefix="/repairs", tags=["Repairs"], dependencies=[Depends(require_role("service_staff", "admin", "staff"))])

@router.post("", response_model=RepairResponse, status_code=status.HTTP_201_CREATED)
def add_repair_history(
    repair_in: RepairCreate,
    db: Session = Depends(get_db)
):
    new_repair = RepairHistory(**repair_in.model_dump())
    db.add(new_repair)
    db.commit()
    db.refresh(new_repair)
    return new_repair
