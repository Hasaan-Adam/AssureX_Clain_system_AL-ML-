"""Comparison Service - Model Comparison & Consistency"""

from typing import Any, Dict, Optional
import yaml
from pathlib import Path

THRESHOLDS_PATH = Path(__file__).resolve().parents[2] / "config" / "thresholds.yaml"
with open(THRESHOLDS_PATH, "r", encoding="utf-8") as f:
    _thresholds = yaml.safe_load(f) or {}

AI_COMP = _thresholds.get("ai_comparison", {})
CONF_THRESH = _thresholds.get("confidence_thresholds", {})

STRONG_MATCH_DELTA = float(AI_COMP.get("strong_match_delta", 0.10))
ACCEPTABLE_DELTA = float(AI_COMP.get("acceptable_delta", 0.20))
WEAK_MATCH_DELTA = float(AI_COMP.get("weak_match_delta", 0.35))
DISAGREEMENT_DELTA = float(AI_COMP.get("disagreement_delta", 0.35))
LOW_CONFIDENCE_THRESHOLD = float(CONF_THRESH.get("low_confidence", 0.60))


class ComparisonService:
    def compare(self, python_prediction: Dict[str, Any], tm_prediction: Optional[Dict[str, Any]] = None, **kwargs: Any) -> Dict[str, Any]:
        return compare_models(python_prediction, tm_prediction, **kwargs)

_comparison_service = ComparisonService()

def get_comparison_service() -> ComparisonService:
    return _comparison_service

def compare_models(
    python_prediction: Dict[str, Any],
    tm_prediction: Optional[Dict[str, Any]] = None,
    rule_prediction: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Compare Python ML, Teachable Machine, and Rule predictions."""
    if tm_prediction and "decision" in tm_prediction and "probabilities" not in tm_prediction and "predicted_class" not in tm_prediction:
        ml_dec = python_prediction.get("decision") or python_prediction.get("predicted_class", "APPROVE")
        rule_dec = tm_prediction.get("decision", "APPROVE")
        passed = tm_prediction.get("passed", True)
        
        agreement = (ml_dec == rule_dec) and passed
        return {
            "agreement": agreement,
            "agreement_score": 1.0 if agreement else 0.0,
            "consensus_decision": ml_dec if agreement else "MANUAL_REVIEW",
            "discrepancy_details": None if agreement else {"ml": ml_dec, "rule": rule_dec},
            "consistency_status": "Strong Match" if agreement else "Disagreement",
            "requires_manual_review": not agreement,
        }

    tm_pred = tm_prediction or kwargs.get("tm_pred") or {}
    
    py_class = python_prediction.get("predicted_class") or python_prediction.get("decision", "Valid Claim")
    tm_class = tm_pred.get("predicted_class") or tm_pred.get("decision", "Valid Claim")
    py_conf = float(python_prediction.get("confidence", 0.0))
    tm_conf = float(tm_pred.get("confidence", 0.0))
    
    py_probs = python_prediction.get("probabilities", {})
    tm_probs = tm_pred.get("probabilities", {})
    
    all_classes = sorted(set(list(py_probs.keys()) + list(tm_probs.keys())))
    deltas = {}
    for c in all_classes:
        deltas[c] = round(abs(py_probs.get(c, 0) - tm_probs.get(c, 0)), 4)
    
    max_delta = round(max(deltas.values()) if deltas else abs(py_conf - tm_conf), 4)
    classes_match = (py_class == tm_class)
    
    if py_conf < LOW_CONFIDENCE_THRESHOLD and tm_conf < LOW_CONFIDENCE_THRESHOLD:
        consistency_status = "Uncertain"
        requires_manual_review = True
    elif not classes_match or max_delta > DISAGREEMENT_DELTA:
        consistency_status = "Disagreement"
        requires_manual_review = True
    elif max_delta <= STRONG_MATCH_DELTA:
        consistency_status = "Strong Match"
        requires_manual_review = False
    elif max_delta <= ACCEPTABLE_DELTA:
        consistency_status = "Acceptable"
        requires_manual_review = False
    elif max_delta <= WEAK_MATCH_DELTA:
        consistency_status = "Weak"
        requires_manual_review = True
    else:
        consistency_status = "Disagreement"
        requires_manual_review = True
    
    all_agree = classes_match and not requires_manual_review
    
    if all_agree:
        consensus_decision = py_class
        discrepancy_details = None
        agreement_score = 1.0
    else:
        consensus_decision = "MANUAL_REVIEW" if "MANUAL" in py_class.upper() or not classes_match else py_class
        if not all_agree:
            consensus_decision = "MANUAL_REVIEW"
        discrepancy_details = {
            "differing_models": [m for m, d in [("Python", py_class), ("TM", tm_class)] if d != py_class]
        }
        agreement_score = round(max(0.0, 1.0 - max_delta), 2)
    
    return {
        "models_evaluated": ["Python ML Model", "Teachable Machine"],
        "agreement": all_agree,
        "agreement_score": agreement_score,
        "consensus_decision": consensus_decision,
        "discrepancy_details": discrepancy_details,
        "python_prediction": python_prediction,
        "tm_prediction": tm_pred,
        "deltas": deltas,
        "max_delta": max_delta,
        "classes_match": classes_match,
        "consistency_status": consistency_status,
        "requires_manual_review": requires_manual_review,
    }