import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

POLICIES_DIR = Path(__file__).resolve().parents[2] / "policies"
_POLICY_CACHE: Dict[str, Dict[str, Any]] = {}

def load_policy(category_code: str) -> Dict[str, Any]:
    """Load JSON policy file for a specific product category with caching."""
    cat = (category_code or "electronics").strip().lower()
    
    # Normalize category name
    if "mob" in cat or "phone" in cat:
        filename = "mobile_phones.json"
    elif "app" in cat or "home" in cat or "refrig" in cat or "wash" in cat:
        filename = "home_appliances.json"
    else:
        filename = "electronics.json"
        
    if filename in _POLICY_CACHE:
        return _POLICY_CACHE[filename]
        
    policy_path = POLICIES_DIR / filename
    if not policy_path.exists():
        # Fallback to default
        policy_path = POLICIES_DIR / "electronics.json"
        
    if policy_path.exists():
        with open(policy_path, "r", encoding="utf-8") as f:
            policy_data = json.load(f)
            _POLICY_CACHE[filename] = policy_data
            return policy_data
            
    # Default fallback object
    return {
        "category_code": category_code.upper() if category_code else "ELECTRONICS",
        "category_name": "General Electronics",
        "grace_period_days": 14,
        "repair_limits": {
            "max_repair_cost_percentage": 75.0,
            "max_claims_per_warranty": 3,
            "total_aggregate_limit_percentage": 100.0,
            "replacement_threshold_percentage": 80.0
        },
        "mandatory_documents": ["purchase_receipt", "product_image"],
        "allowed_fault_types": ["power_failure", "display_defect", "component_failure"],
        "exclusions": [{"code": "LIQUID_DAMAGE", "action": "REJECT"}, {"code": "SCREEN_CRACK_ACCIDENTAL", "action": "REJECT"}],
    }


class RuleEngine:
    def __init__(self, policy: Optional[Dict[str, Any]] = None):
        self.policy = policy

    def evaluate(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        return evaluate_claim_rules(claim_data, self.policy)

    def evaluate_claim(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        return evaluate_claim_rules(claim_data, self.policy)

    def evaluate_rules(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        return evaluate_claim_rules(claim_data, self.policy)



def evaluate_claim_rules(claim_data: Dict[str, Any], policy: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Evaluate claim rules with dynamic category policy lookup."""
    cat = claim_data.get("product_category") or claim_data.get("category") or "electronics"
    active_policy = policy or load_policy(cat)
    
    grace_days = active_policy.get("grace_period_days", 14)
    exclusions_list = active_policy.get("exclusions", [])
    
    violations = []
    warnings = []
    rule_breakdown = []
    
    # 1. Warranty Active & Grace Period Check
    warranty_active = claim_data.get("warranty_active") == "yes" or claim_data.get("warranty_status") == "ACTIVE"
    remaining_days = claim_data.get("remaining_warranty_days", 0)
    is_grace = claim_data.get("is_grace_period", 0)
    
    if not warranty_active and remaining_days < -grace_days and not is_grace:
        violations.append("POLICY_EXPIRED_WARRANTY: Warranty expired beyond grace period")
        rule_breakdown.append({
            "rule": "warranty_coverage_validity",
            "passed": False,
            "action": "REJECT",
            "detail": f"Warranty expired beyond {grace_days}-day grace period"
        })
    elif remaining_days < 0 or is_grace:
        warnings.append("POLICY_GRACE_PERIOD: Within grace period")
        rule_breakdown.append({
            "rule": "warranty_coverage_validity",
            "passed": True,
            "action": "MANUAL_REVIEW",
            "detail": "Within grace period"
        })
    else:
        rule_breakdown.append({
            "rule": "warranty_coverage_validity",
            "passed": True,
            "action": "NONE",
            "detail": "Warranty active"
        })
    
    # 2. Excluded Damage & Policy Exclusions Check
    damage_type = (claim_data.get("damage_type") or "").lower()
    excluded_flag = claim_data.get("excluded_damage") == "yes"
    covered_fault = claim_data.get("covered_fault") == "yes" or (claim_data.get("covered_fault") is None and not excluded_flag)
    
    is_explicit_exclusion = False
    exclusion_action = "REJECT"
    for excl in exclusions_list:
        code = excl.get("code", "").lower()
        if code and code in damage_type:
            is_explicit_exclusion = True
            exclusion_action = excl.get("action", "REJECT").upper()
            break

    if is_explicit_exclusion and exclusion_action == "MANUAL_REVIEW":
        warnings.append("POLICY_EXCLUSION_REVIEW: Damage condition requires manual review")
        rule_breakdown.append({
            "rule": "policy_exclusions_check",
            "passed": True,
            "action": "MANUAL_REVIEW",
            "detail": "Damage condition requires reviewer verification"
        })
    elif excluded_flag or not covered_fault or is_explicit_exclusion:
        violations.append("POLICY_EXCLUDED_DAMAGE: Damage type excluded from coverage")
        rule_breakdown.append({
            "rule": "policy_exclusions_check",
            "passed": False,
            "action": "REJECT",
            "detail": "Excluded damage type detected"
        })
    else:
        rule_breakdown.append({
            "rule": "policy_exclusions_check",
            "passed": True,
            "action": "NONE",
            "detail": "Covered fault type"
        })
    
    # 3. Unauthorized Repair Check
    repair_count = claim_data.get("repair_history_count", 0)
    repair_auth = str(claim_data.get("repair_authorized", "yes")).lower()
    if repair_count > 0 and repair_auth in ("unauthorized", "no", "false"):
        violations.append("UNAUTHORIZED_REPAIR: Product was serviced by unauthorized center")
        rule_breakdown.append({
            "rule": "unauthorized_repair_check",
            "passed": False,
            "action": "REJECT",
            "detail": "Prior unauthorized repairs detected"
        })
        
    # 4. Serial Number Check
    serial_status = claim_data.get("serial_status", "match")
    if serial_status == "mismatch":
        violations.append("POLICY_SERIAL_MISMATCH: Serial number mismatch")
        rule_breakdown.append({
            "rule": "serial_number_verification",
            "passed": False,
            "action": "REJECT",
            "detail": "Serial mismatch"
        })
    elif serial_status == "missing_evidence":
        warnings.append("POLICY_SERIAL_UNREADABLE: Serial evidence missing")
        rule_breakdown.append({
            "rule": "serial_number_verification",
            "passed": False,
            "action": "MANUAL_REVIEW",
            "detail": "Serial evidence missing"
        })
    else:
        rule_breakdown.append({
            "rule": "serial_number_verification",
            "passed": True,
            "action": "NONE",
            "detail": "Serial match"
        })
    
    # 5. Reporting Window Check
    reporting_days = claim_data.get("claim_reporting_days", 0)
    within_period = claim_data.get("within_reporting_period") != "no"
    if reporting_days > 45 or not within_period:
        violations.append("POLICY_REPORTING_DEADLINE_EXCEEDED")
        rule_breakdown.append({
            "rule": "reporting_window_check",
            "passed": False,
            "action": "REJECT",
            "detail": "Reported after maximum deadline"
        })
    elif reporting_days > 30:
        warnings.append("POLICY_REPORTING_DEADLINE_WARNING")
        rule_breakdown.append({
            "rule": "reporting_window_check",
            "passed": True,
            "action": "MANUAL_REVIEW",
            "detail": "Reported near deadline"
        })
    else:
        rule_breakdown.append({
            "rule": "reporting_window_check",
            "passed": True,
            "action": "NONE",
            "detail": "Within reporting window"
        })
    
    # 6. Missing Mandatory Documents Check
    missing_docs = claim_data.get("missing_document_count", 0)
    receipt_avail = claim_data.get("receipt_available") != "no"
    proof = str(claim_data.get("proof_of_purchase", "yes")).lower()
    
    if missing_docs > 0 or not receipt_avail or proof == "no":
        if missing_docs >= 2 or proof == "no":
            warnings.append(f"DOCS_INCOMPLETE: {missing_docs} documents missing")
        rule_breakdown.append({
            "rule": "mandatory_documents_check",
            "passed": False,
            "action": "MANUAL_REVIEW",
            "detail": f"{missing_docs} missing documents or uncertain proof"
        })
    else:
        rule_breakdown.append({
            "rule": "mandatory_documents_check",
            "passed": True,
            "action": "NONE",
            "detail": "All documents present"
        })
    
    # Final Decision Synthesis
    if violations:
        decision = "REJECT"
        passed = False
    elif warnings:
        decision = "MANUAL_REVIEW"
        passed = False
    else:
        decision = "APPROVE"
        passed = True
    
    return {
        "decision": decision,
        "passed": passed,
        "violations": violations,
        "warnings": warnings,
        "violation_count": len(violations),
        "warning_count": len(warnings),
        "rule_breakdown": rule_breakdown,
        "policy_used": active_policy.get("category_code"),
    }


def evaluate_rules(claim_data: Dict[str, Any]) -> Dict[str, Any]:
    """Alias for evaluate_claim_rules."""
    return evaluate_claim_rules(claim_data)