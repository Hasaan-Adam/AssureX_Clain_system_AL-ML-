"""
AssureX Claim Engine - Analytics API Router
Provides endpoints for trend analytics, fault distributions, brand reliability, and fraud insights.
"""

from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database.session import get_db
from src.dependencies import require_role
from src.schemas.analytics import (
    AnalyticsOverviewResponse,
    BrandReliabilityItem,
    FaultDistributionItem,
    FraudDetectionStats,
    TimeSeriesPoint,
)
from src.services import analytics_service
from src.utils.constants import RoleEnum

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview", response_model=AnalyticsOverviewResponse)
def get_analytics_overview(
    current_user = Depends(require_role(RoleEnum.STAFF)),
    db: Session = Depends(get_db),
):
    """Retrieve full analytics overview (time series, faults, brand reliability, fraud)."""
    return analytics_service.get_analytics_overview(db)


@router.get("/trends", response_model=List[TimeSeriesPoint])
def get_trends(
    days: int = Query(30, ge=7, le=180, description="Trailing number of days"),
    current_user = Depends(require_role(RoleEnum.STAFF)),
    db: Session = Depends(get_db),
):
    """Retrieve time-series volume trends."""
    return analytics_service.get_time_series_claims(db, days=days)


@router.get("/faults", response_model=List[FaultDistributionItem])
def get_fault_distribution(
    current_user = Depends(require_role(RoleEnum.STAFF)),
    db: Session = Depends(get_db),
):
    """Retrieve fault type distribution."""
    return analytics_service.get_fault_distribution(db)


@router.get("/reliability", response_model=List[BrandReliabilityItem])
def get_brand_reliability(
    current_user = Depends(require_role(RoleEnum.STAFF)),
    db: Session = Depends(get_db),
):
    """Retrieve brand reliability ratings."""
    return analytics_service.get_brand_reliability_index(db)


@router.get("/fraud", response_model=FraudDetectionStats)
def get_fraud_statistics(
    current_user = Depends(require_role(RoleEnum.REVIEWER)),
    db: Session = Depends(get_db),
):
    """Retrieve fraud detection stats and risk breakdowns."""
    return analytics_service.get_fraud_detection_stats(db)
