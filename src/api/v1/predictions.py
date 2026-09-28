"""
AssureX Claim Engine - AI Predictions & Model Evaluation API Router
Provides endpoints for executing AI inference, batch evaluations, and consensus inspections.
"""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from database.session import get_db
from src.dependencies import get_current_user, require_role
from src.models.claim import Claim
from src.models.prediction import Prediction
from src.models.user import User
from src.schemas.prediction import (
    BatchPredictionRequest,
    BatchPredictionResponse,
    ModelComparisonResponse,
    PredictionResponse,
)
from src.services import prediction_service, rule_engine
from src.utils.constants import RoleEnum

router = APIRouter(prefix="/predictions", tags=["Predictions"])


@router.post("/evaluate/{claim_id}", response_model=Dict[str, Any])
@router.post("/adjudicate/{claim_id}", response_model=Dict[str, Any])
def evaluate_single_claim(
    claim_id: int,
    current_user: User = Depends(require_role(RoleEnum.SERVICE_STAFF, RoleEnum.ADMIN, RoleEnum.REVIEWER, RoleEnum.CUSTOMER)),
    db: Session = Depends(get_db),
):
    """Trigger on-demand AI and rule adjudication for a claim."""
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        return {"error": f"Claim {claim_id} not found."}

    claim_data = {
        "claim_id": claim.claim_id,
        "fault_type": claim.fault_type,
        "fault_description": claim.fault_description,
        "damage_type": claim.damage_type,
        "claim_amount": claim.claim_amount,
        "incident_date": str(claim.fault_occurrence_date or claim.claim_submission_date),
    }
    return prediction_service.adjudicate_claim(db, claim_id=claim.id, claim_data=claim_data)


@router.get("/{claim_id}", response_model=List[PredictionResponse])
@router.get("/claim/{claim_id}", response_model=List[PredictionResponse])
def get_claim_predictions(
    claim_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve all historical AI prediction logs for a claim."""
    predictions = (
        db.query(Prediction)
        .filter(Prediction.claim_id == claim_id)
        .order_by(Prediction.created_at.desc())
        .all()
    )
    return predictions


@router.post("/batch", response_model=BatchPredictionResponse)
def batch_predict(
    payload: BatchPredictionRequest,
    current_user: User = Depends(require_role(RoleEnum.REVIEWER)),
):
    """Run batch inferences on a list of raw claim dictionaries."""
    try:
        from src.ml.predict import batch_predict_claims
        results = batch_predict_claims(payload.claims)
    except Exception:
        results = []
        for c in payload.claims:
            r = rule_engine.evaluate_claim_rules(c)
            results.append({
                "predicted_class": "Valid Claim" if r["decision"] == "APPROVE" else "Invalid Claim",
                "confidence": 0.88,
                "probabilities": {"Valid Claim": 0.88, "Invalid Claim": 0.12},
                "model_version": "v1.0.0-fallback",
            })

    return {"total": len(results), "predictions": results}

