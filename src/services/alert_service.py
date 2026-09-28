"""Alert Service - System Monitoring and Anomaly Detection"""

from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime, timedelta

from database.models import Claim, User, Warranty, Document, Prediction, AuditLog


def check_system_anomalies(db: Session) -> List[Dict[str, Any]]:
    """Check for live system anomalies across claims, documents, predictions, and models."""
    alerts = []
    
    try:
        unverified_docs = db.query(Document).filter(
            Document.is_verified == False,
            Document.created_at >= datetime.utcnow() - timedelta(hours=24)
        ).count()
        if unverified_docs > 15:
            alerts.append({
                "type": "unverified_uploads_backlog",
                "count": unverified_docs,
                "severity": "medium",
                "message": f"{unverified_docs} documents pending verification in the last 24h"
            })
    except Exception:
        pass

    try:
        duplicate_hashes = (
            db.query(Document.file_hash, func.count(Document.id).label("hash_count"))
            .group_by(Document.file_hash)
            .having(func.count(Document.id) > 1)
            .all()
        )
        if duplicate_hashes:
            total_duplicates = len(duplicate_hashes)
            alerts.append({
                "type": "duplicate_documents_detected",
                "count": total_duplicates,
                "severity": "high",
                "message": f"{total_duplicates} duplicate document hash clusters detected"
            })
    except Exception:
        pass

    try:
        recent_claims = db.query(Claim).filter(
            Claim.claim_submission_date >= date.today() - timedelta(days=1)
        ).count()
        if recent_claims > 100:
            alerts.append({
                "type": "high_claim_volume",
                "count": recent_claims,
                "severity": "high",
                "message": f"Claim volume surge: {recent_claims} claims submitted in the last 24h"
            })
    except Exception:
        pass

    try:
        recent_claims = db.query(Claim).filter(
            Claim.claim_submission_date >= date.today() - timedelta(days=1)
        ).all()
        high_fraud_count = sum(1 for c in recent_claims if (c.fraud_score or 0) >= 0.70)
        if high_fraud_count >= 3:
            alerts.append({
                "type": "fraud_spike",
                "count": high_fraud_count,
                "severity": "critical",
                "message": f"Fraud spike: {high_fraud_count} claims with elevated risk (>=0.70) in 24h"
            })
    except Exception:
        pass

    try:
        total_predictions = db.query(Prediction).count()
        if total_predictions >= 5:
            disagreement_count = db.query(Prediction).filter(
                Prediction.model_consistency_status.in_(["Disagreement", "Weak Match", "Model Disagreement"])
            ).count()
            disagreement_rate = (disagreement_count / total_predictions) * 100
            if disagreement_rate > 25.0:
                alerts.append({
                    "type": "excessive_model_disagreement",
                    "count": disagreement_count,
                    "severity": "medium",
                    "message": f"Model disagreement rate is {disagreement_rate:.1f}% ({disagreement_count}/{total_predictions} predictions)"
                })
    except Exception:
        pass

    return alerts


def get_anomaly_alerts(db: Session) -> List[Dict[str, Any]]:
    """Get current anomaly alerts."""
    return check_system_anomalies(db)