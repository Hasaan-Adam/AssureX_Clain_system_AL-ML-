"""
Analytics Service - Claim Analytics & Fraud Reporting

Every figure returned here is computed from the live database. No metric is
hard-coded or estimated, as required by the SRS (no fabricated results).
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import date, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from database.models import Claim, Prediction, Product, Warranty

APPROVED_STATUSES = ("approved", "auto_approved", "settled")
REJECTED_STATUSES = ("rejected",)
PENDING_STATUSES = (
    "submitted",
    "under_review",
    "under_evaluation",
    "manual_review",
    "info_required",
    "escalated",
    "appeal_requested",
)


def _status_counts(claims: List[Claim]) -> Dict[str, int]:
    counts: Counter = Counter()
    for claim in claims:
        status = (claim.status or "").lower()
        if status in APPROVED_STATUSES:
            counts["approved"] += 1
        elif status in REJECTED_STATUSES:
            counts["rejected"] += 1
        elif status in PENDING_STATUSES:
            counts["under_review"] += 1
    return dict(counts)


def get_analytics_overview(db: Session) -> Dict[str, Any]:
    """Aggregate analytics overview assembled from the individual reports."""
    return {
        "time_series": get_time_series_claims(db, days=30),
        "fault_distribution": get_fault_distribution(db),
        "brand_reliability": get_brand_reliability_index(db),
        "fraud_stats": get_fraud_detection_stats(db),
    }


def get_fault_distribution(db: Session) -> List[Dict[str, Any]]:
    """Fault-type distribution across all claims, with percentage share."""
    claims = db.query(Claim).all()
    total = len(claims)
    fault_counts = Counter((c.fault_type or "unspecified") for c in claims)
    return [
        {
            "fault_type": fault_type,
            "count": count,
            "percentage": round((count / total) * 100, 2) if total else 0.0,
        }
        for fault_type, count in fault_counts.most_common(10)
    ]


def get_brand_reliability_index(db: Session) -> List[Dict[str, Any]]:
    """
    Brand reliability index (SRS: reliability score derived from claim rate).
    reliability_score = 100 - claim_rate, so fewer claims means better score.
    """
    warranties = db.query(Warranty).all()
    products = {p.id: p for p in db.query(Product).all()}

    stats: Dict[str, Dict[str, int]] = {}
    for warranty in warranties:
        product = products.get(warranty.product_id)
        brand = (product.brand if product else None) or "Unknown"
        entry = stats.setdefault(brand, {"total_warranties": 0, "total_claims": 0})
        entry["total_warranties"] += 1

    for claim in db.query(Claim).all():
        product = products.get(claim.product_id)
        brand = (product.brand if product else None) or "Unknown"
        entry = stats.setdefault(brand, {"total_warranties": 0, "total_claims": 0})
        entry["total_claims"] += 1

    results = []
    for brand, entry in stats.items():
        warranties_count = entry["total_warranties"]
        claims_count = entry["total_claims"]
        claim_rate = (claims_count / warranties_count) if warranties_count else 0.0
        results.append(
            {
                "brand": brand,
                "total_warranties": warranties_count,
                "total_claims": claims_count,
                "claim_rate_percentage": round(claim_rate * 100, 2),
                "reliability_score": round(max(0.0, 100.0 - claim_rate * 100), 2),
            }
        )

    results.sort(key=lambda item: item["reliability_score"], reverse=True)
    return results


def get_fraud_detection_stats(db: Session, risk_threshold: float = 0.5) -> Dict[str, Any]:
    """
    Fraud statistics derived from the stored fraud scores.
    Risk bands: >=0.7 high, >=0.4 medium, otherwise low.
    """
    claims = db.query(Claim).all()
    all_scores = [float(claim.fraud_score or 0.0) for claim in claims]

    high = [score for score in all_scores if score >= 0.7]
    medium = [score for score in all_scores if 0.4 <= score < 0.7]
    low = [score for score in all_scores if score < 0.4]
    flagged = [score for score in all_scores if score >= risk_threshold]

    predictions = db.query(Prediction).all()
    indicators: Counter = Counter()
    for prediction in predictions:
        for reason in _fraud_reasons(prediction) or []:
            indicators[reason] += 1

    total = len(all_scores)
    return {
        "total_flagged_claims": len(flagged),
        "average_fraud_score": round(sum(all_scores) / total, 4) if total else 0.0,
        "high_risk_claims_count": len(high),
        "medium_risk_claims_count": len(medium),
        "low_risk_claims_count": len(low),
        "top_fraud_indicators": [
            {"indicator": name, "count": count} for name, count in indicators.most_common(5)
        ],
    }


def get_time_series_claims(db: Session, days: int = 30) -> List[Dict[str, Any]]:
    """
    Dense daily series (one entry per day, zero-filled) so charts never have
    gaps, with per-day approved / rejected / under-review counts.
    """
    start = date.today() - timedelta(days=days - 1)
    claims = db.query(Claim).all()

    buckets: Dict[date, List[Claim]] = {start + timedelta(days=i): [] for i in range(days)}
    for claim in claims:
        claim_date = claim.claim_submission_date
        if claim_date and claim_date in buckets:
            buckets[claim_date].append(claim)

    series = []
    for day, day_claims in buckets.items():
        counts = _status_counts(day_claims)
        series.append(
            {
                "date": day.isoformat(),
                "total_claims": len(day_claims),
                "approved": counts.get("approved", 0),
                "rejected": counts.get("rejected", 0),
                "under_review": counts.get("under_review", 0),
            }
        )
    return series


def _fraud_reasons(prediction: Prediction) -> Optional[List[str]]:
    """Extract fraud indicator labels recorded on a prediction row."""
    for raw in (
        getattr(prediction, "fraud_reasons", None),
        _load_json(getattr(prediction, "rule_engine_result", None)),
        _load_json(getattr(prediction, "comparison_result", None)),
    ):
        if isinstance(raw, list) and raw:
            return [str(item) for item in raw]
    return None


def _load_json(raw: Any) -> Any:
    if not raw:
        return None
    if isinstance(raw, (dict, list)):
        return raw
    try:
        return json.loads(raw)
    except (TypeError, ValueError):
        return None


def get_claim_analytics(db: Session, user_id: Optional[int] = None) -> Dict[str, Any]:
    """Per-claim analytics used by the dashboards (scoped to one customer)."""
    query = db.query(Claim)
    if user_id is not None:
        query = query.filter(Claim.claimant_id == user_id)
    claims = query.all()

    counts = _status_counts(claims)
    total = len(claims)
    amounts = [float(c.claim_amount or 0.0) for c in claims]

    return {
        "total_claims": total,
        "approved_claims": counts.get("approved", 0),
        "rejected_claims": counts.get("rejected", 0),
        "pending_claims": counts.get("under_review", 0),
        "total_claimed_amount": round(sum(amounts), 2),
        "average_claim_amount": round(sum(amounts) / total, 2) if total else 0.0,
        "approval_rate": round((counts.get("approved", 0) / total) * 100, 2) if total else 0.0,
    }
