from typing import Any, Dict, List, Optional, Tuple
from src.utils.constants import DecisionType


def aggregate_decision(
    ml_confidence: float = 0.90,
    fraud_score: float = 0.0,
    rule_passed: bool = True,
    **kwargs: Any,
) -> Dict[str, Any]:

    """Aggregate high-level decision based on ML confidence, fraud score, and rule pass flag."""
    if not rule_passed or fraud_score >= 0.70:
        return {"decision": DecisionType.REJECT.value, "reason": "Rule violation or high fraud risk"}
    elif fraud_score >= 0.30 or ml_confidence < 0.80:
        return {"decision": DecisionType.MANUAL_REVIEW.value, "reason": "Elevated risk score or low confidence"}
    else:
        return {"decision": DecisionType.APPROVE.value, "reason": "High confidence clean claim"}


def adjudicate_claim(claim_data: Dict[str, Any]) -> Dict[str, Any]:
    """End-to-end adjudication of claim data payload."""
    from src.services.rule_engine import RuleEngine
    from src.services.contradiction_service import ContradictionService
    from src.services.prediction_service import predict_tabular_claim
    
    rule_eng = RuleEngine()
    rule_res = rule_eng.evaluate_claim(claim_data)
    
    # ML Tabular prediction
    ml_res = predict_tabular_claim(claim_data)
    pred_class = ml_res.get("predicted_class", "Valid Claim")
    confidence = ml_res.get("confidence", 0.90)
    
    # Excluded damage check
    excluded = claim_data.get("excluded_damage") == "yes" or claim_data.get("damage_type") in ("PHYSICAL_IMPACT", "LIQUID_SPILL", "UNAUTHORIZED_REPAIR")
    
    if rule_res.get("violation_count", 0) > 0 or excluded:
        final_dec = "Invalid Claim"
        req_review = False
        reason = "Claim rejected due to policy exclusions or rule violations."
    elif pred_class == "Manual Review" or confidence < 0.75:
        final_dec = "Manual Review"
        req_review = True
        reason = "Claim requires manual adjudicator review."
    elif pred_class == "Invalid Claim":
        final_dec = "Invalid Claim"
        req_review = False
        reason = "Claim predicted invalid by adjudication models."
    else:
        final_dec = "Valid Claim"
        req_review = False
        reason = "Claim successfully validated and meets all warranty criteria."
        
    return {
        "final_decision": final_dec,
        "confidence": confidence,
        "requires_human_review": req_review,
        "primary_reason": reason,
        "risk_flags": rule_res.get("violations", []),
        "rule_evaluation": rule_res,
        "ml_prediction": ml_res,
    }


class DecisionService:
    def synthesize_decision(
        self,
        python_prediction: Dict[str, Any],
        tm_prediction: Dict[str, Any],
        comparison_result: Dict[str, Any],
        rule_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        return make_final_decision_full(python_prediction, tm_prediction, comparison_result, rule_result)

    def aggregate_decision(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return aggregate_decision(*args, **kwargs)

    def adjudicate_claim(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        return adjudicate_claim(claim_data)

_decision_service = DecisionService()

def get_decision_service() -> DecisionService:
    return _decision_service


def generate_claim_executive_summary(claim_data: Dict[str, Any], final_result: Optional[Dict[str, Any]] = None) -> str:
    """Generate executive textual summary for claim report."""
    outcome = final_result.get('final_decision', '') if final_result else 'Evaluated'
    return f"Claim {claim_data.get('claim_id', '')} adjudicated with outcome: {outcome}."



def make_final_decision(
    python_prediction: Dict[str, Any],
    tm_prediction: Dict[str, Any],
    comparison_result: Dict[str, Any],
    rule_result: Dict[str, Any],
) -> str:
    """Synthesize final decision from all signals."""
    py_class = python_prediction.get("predicted_class", "")
    tm_class = tm_prediction.get("predicted_class", "")
    py_conf = python_prediction.get("confidence", 0.0)
    tm_conf = tm_prediction.get("confidence", 0.0)
    
    rule_decision = rule_result.get("decision", DecisionType.MANUAL_REVIEW.value)
    rule_violations = rule_result.get("violation_count", 0)
    rule_warnings = rule_result.get("warning_count", 0)
    
    consistency = comparison_result.get("consistency_status", "Disagreement")
    requires_manual = comparison_result.get("requires_manual_review", True)
    max_delta = comparison_result.get("max_delta", 1.0)
    classes_match = comparison_result.get("classes_match", False)
    
    HIGH_CONF = 0.80
    LOW_CONF = 0.60
    
    # 1. Hard rule violations -> Likely Invalid
    if rule_violations > 0:
        return "Likely Invalid"
    
    # 2. Strong model disagreement -> Manual Review
    if consistency == "Disagreement" or not classes_match:
        return "Manual Review Required"
    
    # 3. Low confidence -> Manual Review
    if py_conf < LOW_CONF or tm_conf < LOW_CONF:
        return "Manual Review Required"
    
    # 4. Rule warnings -> Manual Review
    if rule_warnings > 0:
        return "Manual Review Required"
    
    # 5. Weak consistency -> Manual Review
    if consistency in ("Weak", "Weak Match", "Uncertain") or comparison_result.get("max_delta", 0) > 0.25:
        return "Manual Review Required"
    
    # 6. Strong agreement + rules pass -> Check Predicted Class
    if consistency in ("Strong Match", "Acceptable", "Acceptable Match") and classes_match:
        if "Invalid" in py_class or "Invalid" in tm_class:
            return "Likely Invalid"
        return "Likely Valid"
    
    return "Manual Review Required"


def make_final_decision_full(
    python_prediction: Dict[str, Any],
    tm_prediction: Dict[str, Any],
    comparison_result: Dict[str, Any],
    rule_result: Dict[str, Any],
) -> Dict[str, Any]:
    decision = make_final_decision(python_prediction, tm_prediction, comparison_result, rule_result)
    
    return {
        "final_decision": decision,
        "decision_factors": {
            "rule_violations": rule_result.get("violation_count", 0),
            "rule_warnings": rule_result.get("warning_count", 0),
            "model_consistency": comparison_result.get("consistency_status"),
            "models_match": comparison_result.get("classes_match"),
            "max_confidence_delta": comparison_result.get("max_delta"),
            "python_confidence": python_prediction.get("confidence"),
            "tm_confidence": tm_prediction.get("confidence"),
            "python_class": python_prediction.get("predicted_class"),
            "tm_class": tm_prediction.get("predicted_class"),
            "rule_decision": rule_result.get("decision"),
        },
    }