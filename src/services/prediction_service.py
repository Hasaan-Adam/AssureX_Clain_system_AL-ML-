"""Prediction Service - ML Model Inference & Adjudication"""

from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from database.models import Claim, Prediction
from src.ml.predict import predict_claim
from src.services.tm_service import accept_frontend_tm_result
from src.services.comparison_service import compare_models
from src.services.rule_engine import evaluate_rules
from src.services.decision_service import make_final_decision
from src.core.exceptions import NotFoundError


def predict_tabular_claim(claim_data: Dict[str, Any]) -> Dict[str, Any]:
    """Execute Python Tabular ML prediction on claim feature payload."""
    return predict_claim(claim_data)



def adjudicate_claim(db: Session, claim_id: int, claim_data: Dict[str, Any]) -> Dict[str, Any]:
    """Run full adjudication pipeline for a claim using trained ML models and Rule Engine."""
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise NotFoundError("Claim", claim_id)
    
    prod = claim.product
    warranty = claim.warranty

    import json
    from database.models import RepairHistory
    from src.services.contradiction_service import detect_contradictions

    # Query real repair history from database if available
    prior_repairs = db.query(RepairHistory).join(Claim, RepairHistory.claim_id == Claim.id).filter(Claim.product_id == claim.product_id).all() if claim.product_id else []
    repair_count = len(prior_repairs) if prior_repairs else int(claim_data.get("repair_history_count") or 0)
    repair_auth = "no" if any(r.authorized_status == "no" for r in prior_repairs) else claim_data.get("repair_authorized", "yes")

    # Enrich dictionary with all product and warranty facts for ML model and rule engine
    enriched_data = dict(claim_data)
    enriched_data["claim_id"] = claim.claim_id
    enriched_data["product_id"] = claim.product_id
    enriched_data["product_category"] = prod.category if prod else "electronics"
    enriched_data["product_name"] = prod.name if prod else "Smart Display"
    enriched_data["brand"] = prod.brand if prod else "Samsung"
    enriched_data["purchase_price"] = float(prod.purchase_price) if prod and prod.purchase_price else float(claim.claim_amount or 0.0)
    enriched_data["purchase_date"] = str(prod.purchase_date if prod and prod.purchase_date else (warranty.start_date if warranty else datetime.utcnow().date()))
    enriched_data["warranty_start_date"] = str(warranty.start_date if warranty else datetime.utcnow().date())
    enriched_data["warranty_expiry_date"] = str(warranty.expiry_date if warranty else datetime.utcnow().date())
    enriched_data["warranty_duration_months"] = getattr(prod, "warranty_duration_months", 12)
    enriched_data["fault_occurrence_date"] = str(claim.fault_occurrence_date or datetime.utcnow().date())
    enriched_data["claim_submission_date"] = str(claim.claim_submission_date or datetime.utcnow().date())
    enriched_data["fault_type"] = claim.fault_type
    enriched_data["damage_type"] = claim.damage_type or "component_failure"
    enriched_data["retailer"] = prod.retailer if prod else "Authorized Store"
    enriched_data["warranty_type"] = prod.warranty_type if prod else "standard"
    enriched_data["repair_history_count"] = repair_count
    enriched_data["repair_authorized"] = repair_auth
    
    # Detect real logical contradictions
    contradiction_eval = detect_contradictions(enriched_data)
    enriched_data["contradiction_type"] = contradiction_eval.get("contradiction_type", "none")
    enriched_data["ocr_quality"] = "high" if claim.documents else "missing"
    
    # 1. Python ML Prediction (using trained XGBoost/RandomForest)
    py_result = predict_claim(enriched_data)
    
    # 2. TM Prediction (Vision Model / Dual Consensus)
    tm_result = claim_data.get("tm_prediction", {})
    if tm_result:
        tm_result = accept_frontend_tm_result(tm_result)
    else:
        # Generate actual TM vision inference using trained model weights
        from src.services.tm_service import get_tm_model
        tm_model = get_tm_model()
        tm_result = tm_model.predict_from_features(enriched_data)
    
    # 3. Model Comparison
    comparison = compare_models(py_result, tm_result)
    
    # 4. Rule Engine
    rule_result = evaluate_rules(enriched_data)
    
    # 5. Final Decision
    final_decision = make_final_decision(py_result, tm_result, comparison, rule_result)
    
    # Save prediction record with clean JSON serialization
    prediction = Prediction(
        claim_id=claim_id,
        python_predicted_class=py_result.get("predicted_class"),
        python_probabilities=json.dumps(py_result.get("probabilities", {})),
        tm_predicted_class=tm_result.get("predicted_class"),
        tm_probabilities=json.dumps(tm_result.get("probabilities", {})),
        comparison_result=json.dumps(comparison),
        model_consistency_status=comparison.get("consistency_status"),
        rule_decision=rule_result.get("decision"),
        rule_breakdown=json.dumps(rule_result.get("rule_breakdown", {})),
        final_decision=final_decision,
        model_versions=json.dumps({
            "python": py_result.get("model_version"),
            "tm": tm_result.get("model_version"),
        }),
    )
    db.add(prediction)
    
    # Update claim
    claim.python_prediction = py_result.get("predicted_class")
    claim.python_confidence = json.dumps(py_result.get("probabilities", {}))
    claim.tm_prediction = tm_result.get("predicted_class")
    claim.tm_confidence = json.dumps(tm_result.get("probabilities", {}))
    claim.comparison_result = json.dumps(comparison)
    claim.rule_engine_result = json.dumps(rule_result)
    claim.final_decision = final_decision
    claim.python_model_version = py_result.get("model_version")
    claim.tm_model_version = tm_result.get("model_version")
    claim.status = "under_review" if final_decision == "Manual Review Required" else "approved" if final_decision == "Likely Valid" else "rejected"
    claim.decided_at = datetime.utcnow()
    
    db.commit()
    
    db.commit()
    
    return {
        "python_prediction": py_result,
        "tm_prediction": tm_result,
        "comparison": comparison,
        "rule_result": rule_result,
        "final_decision": final_decision,
    }


def calculate_fraud_risk(claim_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate fraud risk score."""
    risk_score = 0.0
    factors = []
    
    if claim_data.get("is_duplicate") == "yes":
        risk_score += 0.5
        factors.append("Duplicate claim detected")
    if claim_data.get("serial_status") == "mismatch":
        risk_score += 0.3
        factors.append("Serial number mismatch")
    if claim_data.get("has_contradiction") == "yes":
        risk_score += 0.2
        factors.append("Data contradiction")
    
    return {
        "risk_score": min(risk_score, 1.0),
        "level": "high" if risk_score > 0.7 else "medium" if risk_score > 0.3 else "low",
        "factors": factors,
    }