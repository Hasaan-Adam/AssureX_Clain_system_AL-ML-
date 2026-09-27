"""
AssureX Claim Engine - Analytics Pydantic Schemas
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class TimeSeriesPoint(BaseModel):
    date: str
    total_claims: int
    approved: int
    rejected: int
    under_review: int


class FaultDistributionItem(BaseModel):
    fault_type: str
    count: int
    percentage: float


class BrandReliabilityItem(BaseModel):
    brand: str
    total_warranties: int
    total_claims: int
    claim_rate_percentage: float
    reliability_score: float # 0.0 to 100.0


class FraudDetectionStats(BaseModel):
    total_flagged_claims: int
    average_fraud_score: float
    high_risk_claims_count: int
    medium_risk_claims_count: int
    low_risk_claims_count: int
    top_fraud_indicators: List[Dict[str, Any]] = []


class AnalyticsOverviewResponse(BaseModel):
    time_series: List[TimeSeriesPoint]
    fault_distribution: List[FaultDistributionItem]
    brand_reliability: List[BrandReliabilityItem]
    fraud_stats: FraudDetectionStats