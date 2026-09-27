"""
AssureX Claim Engine - AI Prediction Pydantic Schemas
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PredictionBase(BaseModel):
    model_config = {'protected_namespaces': ()}
    model_name: str
    prediction_result: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    fraud_risk_score: float = Field(0.0, ge=0.0, le=1.0)
    feature_importance: Optional[Dict[str, Any]] = None
    raw_output: Optional[Dict[str, Any]] = None


class PredictionCreate(PredictionBase):
    claim_id: int


class PredictionResponse(BaseModel):
    model_config = {'protected_namespaces': (), 'from_attributes': True}
    id: int
    claim_id: int
    model_name: Optional[str] = "Dual AI Ensemble (XGBoost + Teachable Machine)"
    prediction_result: Optional[str] = "Likely Valid"
    confidence_score: Optional[float] = 0.95
    fraud_risk_score: Optional[float] = 0.0
    feature_importance: Optional[Dict[str, Any]] = None
    raw_output: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None


class BatchPredictionRequest(BaseModel):
    claims: List[Dict[str, Any]]


class BatchPredictionResponse(BaseModel):
    total: int
    predictions: List[Dict[str, Any]]


class ModelComparisonResponse(BaseModel):
    claim_id: int
    python_model_decision: str
    python_model_confidence: float
    rule_engine_decision: str
    final_adjudication: str
    agreement: bool
    agreement_score: float
    discrepancy_details: Optional[Dict[str, Any]] = None