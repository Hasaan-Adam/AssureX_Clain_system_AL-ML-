"""
AssureX Claim Engine - Dashboard Pydantic Schemas
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class StatusCountItem(BaseModel):
    status: str
    count: int


class UserDashboardStats(BaseModel):
    total_warranties: int
    active_warranties: int
    expiring_soon_warranties: int
    total_claims: int
    approved_claims: int
    pending_claims: int
    rejected_claims: int
    claims_by_status: Dict[str, int] = {}
    pending_actions: List[Dict[str, Any]] = []
    recent_claims: List[Dict[str, Any]] = []


class AdminDashboardStats(BaseModel):
    total_claims: int
    today_claims: int
    pending_reviews: int
    approved_claims: int
    rejected_claims: int
    approval_rate: float
    rejection_rate: float
    manual_review_rate: float
    total_warranties: int
    total_users: int
    total_products: int
    average_turnaround_hours: float
    claims_by_status: Dict[str, int] = {}
    claims_by_category: Dict[str, int] = {}
    fraud_flagged_count: int
    human_override_rate: float
    recent_activity: List[Dict[str, Any]] = []