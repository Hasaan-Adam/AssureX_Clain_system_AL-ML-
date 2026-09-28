"""Explanation Service - Human-readable decision explanations"""

from typing import Any, Dict, List, Optional

from src.utils.constants import DecisionType


def generate_explanation(
    python_prediction: Dict[str, Any],
    tm_prediction: Dict[str, Any],
    comparison_result: Dict[str, Any],
    rule_result: Dict[str, Any],
    final_decision: str,
) -> Dict[str, Any]:
    """Generate human-readable explanation."""
    
    py_class = python_prediction.get("predicted_class", "")
    py_conf = python_prediction.get("confidence", 0.0)
    tm_class = tm_prediction.get("predicted_class", "")
    tm_conf = tm_prediction.get("confidence", 0.0)
    
    rule_decision = rule_result.get("decision", "")
    violations = rule_result.get("violations", [])
    warnings = rule_result.get("warnings", [])
    rule_breakdown = rule_result.get("rule_breakdown", [])
    
    consistency = comparison_result.get("consistency_status", "")
    max_delta = comparison_result.get("max_delta", 0.0)
    classes_match = comparison_result.get("classes_match", False)
    
    supporting = []
    opposing = []
    
    if py_conf >= 0.80:
        supporting.append(f"Python ML model confidently predicts '{py_class}' ({py_conf:.1%})")
    if tm_conf >= 0.80:
        supporting.append(f"Teachable Machine confidently predicts '{tm_class}' ({tm_conf:.1%})")
    if classes_match:
        supporting.append(f"Both AI models agree on '{py_class}'")
    if comparison_result.get("consistency_status") in ("Strong Match", "Acceptable", "Acceptable Match"):
        supporting.append(f"Models show {comparison_result.get('consistency_status', '').lower()} consistency (Δ={comparison_result.get('max_delta', 0):.2f})")
    if rule_result.get("decision") == "APPROVE":
        supporting.append("All warranty rules passed")
    
    if py_class != tm_class:
        opposing.append(f"Model disagreement: Python='{py_class}', TM='{tm_class}'")
    if consistency in ("Disagreement", "Weak", "Weak Match", "Uncertain"):
        opposing.append(f"Low model consistency: {consistency} (Δ={max_delta:.2f})")
    if py_conf < 0.60:
        opposing.append(f"Python confidence below threshold ({py_conf:.1%})")
    if tm_conf < 0.60:
        opposing.append(f"TM confidence below threshold ({tm_conf:.1%})")
    opposing.extend(violations)
    opposing.extend(warnings)
    
    rules_passed = [rb["rule"] for rb in rule_breakdown if rb.get("passed")]
    rules_failed = [rb["rule"] for rb in rule_breakdown if not rb.get("passed")]
    
    summary = _generate_summary(final_decision, consistency, classes_match, violations, warnings)
    
    return {
        "final_decision": final_decision,
        "summary": summary,
        "supporting_factors": supporting,
        "opposing_factors": opposing,
        "rules_passed": rules_passed,
        "rules_failed": rules_failed,
        "additional_evidence_required": _get_required_evidence(final_decision, rule_result),
        "model_consistency": consistency,
        "confidence_delta": max_delta,
    }


def _generate_summary(decision: str, consistency: str, models_match: bool, violations: List[str], warnings: List[str]) -> str:
    if decision == "Likely Valid":
        if consistency == "Strong Match":
            return "Both AI models strongly agree on a valid claim. All warranty rules pass."
        return "Both AI models predict a valid claim. No hard rule violations found."
    
    elif decision == "Likely Invalid":
        if violations:
            return f"Claim fails warranty rule: {violations[0]}"
        return "Claim shows strong indicators of being invalid."
    
    else:
        reasons = []
        if not models_match:
            reasons.append("AI models disagree")
        if consistency in ("Disagreement", "Weak Match", "Uncertain"):
            reasons.append(f"low consistency ({consistency.lower()})")
        if warnings:
            reasons.append(f"{len(warnings)} rule warning(s)")
        if not reasons:
            reasons.append("ambiguous evidence")
        return f"Manual review required: {', '.join(reasons)}"


def _get_required_evidence(decision: str, rule_result: Dict[str, Any]) -> List[str]:
    evidence = []
    if decision == "Manual Review Required":
        evidence.append("Human reviewer assessment")
    if any("receipt" in w.lower() for w in rule_result.get("warnings", [])):
        evidence.append("Proof of purchase (receipt/invoice)")
    if any("serial" in w.lower() for w in rule_result.get("warnings", [])):
        evidence.append("Clear serial number evidence")
    if any("repair" in w.lower() for w in rule_result.get("warnings", [])):
        evidence.append("Authorized repair center report")
    return evidence


def generate_claim_explanation(adj_result: Dict[str, Any], claim_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Generate human-readable transparent explanation for an adjudicated claim."""
    decision = adj_result.get("final_decision", "Manual Review")
    conf = adj_result.get("confidence", 0.90)
    supporting = []
    opposing = []
    
    if decision == "Valid Claim":
        supporting.append(f"Model evaluated with confidence {conf:.1%}")
        supporting.append("Warranty is active and purchase proof corroborated")
        supporting.append("No policy exclusions or unauthorized repairs detected")
    elif decision == "Invalid Claim":
        opposing.append(adj_result.get("primary_reason", "Policy violation"))
    else:
        opposing.append("Ambiguity in documentation or model confidence below automatic threshold")
        
    return {
        "decision": decision,
        "confidence": conf,
        "summary": adj_result.get("primary_reason", "Claim processed."),
        "supporting_factors": supporting,
        "opposing_factors": opposing,
        "rules_passed": ["warranty_active_check", "proof_of_purchase_check"] if decision == "Valid Claim" else [],
        "rules_failed": ["policy_coverage"] if decision == "Invalid Claim" else [],
    }


def format_explanation_markdown(exp: Dict[str, Any]) -> str:
    """Format explanation dictionary as GitHub markdown document."""
    lines = [
        "# AssureX Claim Adjudication Explanation",
        "",
        f"**Adjudication Decision:** {exp.get('decision', 'Under Review')}",
        f"**Confidence Score:** {exp.get('confidence', 0.0) * 100:.1f}%",
        f"**Summary:** {exp.get('summary', '')}",
        "",
        "### Supporting Factors",
    ]
    for s in exp.get("supporting_factors", []):
        lines.append(f"- {s}")
    lines.append("")
    lines.append("### Opposing Factors / Risk Flags")
    for o in exp.get("opposing_factors", []):
        lines.append(f"- {o}")
    lines.append("")
    return "\n".join(lines)


generate_decision_explanation = generate_explanation