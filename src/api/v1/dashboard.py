"""
AssureX Claim Engine - Dashboards API Router
Provides consolidated analytics summaries for Customer and Administrator dashboards.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import get_db
from src.dependencies import get_current_user, require_role
from src.models.user import User
from src.schemas.dashboard import AdminDashboardStats, UserDashboardStats
from src.services import dashboard_service
from src.utils.constants import RoleEnum

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/user", response_model=UserDashboardStats)
@router.get("/customer", response_model=UserDashboardStats)
def get_customer_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve personal claims and warranty dashboard metrics for the logged-in customer."""
    return dashboard_service.get_user_dashboard(
        db=db,
        user_id=current_user.id,
    )


@router.get("/admin", response_model=AdminDashboardStats)
def get_administrator_dashboard(
    current_user: User = Depends(require_role("admin", "staff", "service_staff", "reviewer")),
    db: Session = Depends(get_db),
):
    """Retrieve operational metrics, turnaround times, and system volumes for administrators/staff."""
    return dashboard_service.get_admin_dashboard(db)
