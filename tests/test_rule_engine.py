"""Unit tests for AssureX Deterministic Policy & Warranty Rule Engine."""

import pytest
from src.services.rule_engine import (
    RuleEngine,
    evaluate_claim_rules,
    evaluate_rules,
    load_policy,
)
from src.utils.constants import DecisionType


@pytest.fixture
def rule_engine():
    return RuleEngine()


def test_rule_engine_valid_claim(sample_valid_claim_dict):
    """Verify clean valid claim passes all rules."""
    result = evaluate_claim_rules(sample_valid_claim_dict)
    assert result["decision"] == DecisionType.APPROVE.value
    assert result["passed"] is True
    assert len(result["violations"]) == 0


def test_rule_engine_expired_warranty(sample_valid_claim_dict):
    """Verify expired warranty triggers rejection violation."""
    claim = dict(sample_valid_claim_dict)
    claim["warranty_active"] = "no"
    claim["remaining_warranty_days"] = -60
    claim["is_grace_period"] = 0

    result = evaluate_claim_rules(claim)
    assert result["decision"] == DecisionType.REJECT.value
    assert any("POLICY_EXPIRED_WARRANTY" in v for v in result["violations"])


def test_rule_engine_excluded_damage(sample_valid_claim_dict):
    """Verify excluded damage triggers rejection."""
    claim = dict(sample_valid_claim_dict)
    claim["damage_type"] = "liquid_damage"
    claim["excluded_damage"] = "yes"

    result = evaluate_claim_rules(claim)
    assert result["decision"] == DecisionType.REJECT.value
    assert any("POLICY_EXCLUDED_DAMAGE" in v for v in result["violations"])


def test_rule_engine_missing_docs_warning(sample_valid_claim_dict):
    """Verify missing documentation triggers manual review."""
    claim = dict(sample_valid_claim_dict)
    claim["missing_document_count"] = 3
    claim["receipt_available"] = "no"
    claim["proof_of_purchase"] = "no"

    result = evaluate_claim_rules(claim)
    assert result["decision"] == DecisionType.MANUAL_REVIEW.value


def test_load_policy_all_categories(rule_engine):
    """Verify loading policy JSON schemas for all standard categories."""
    p_elec = load_policy("electronics")
    assert p_elec["category_code"] == "ELECTRONICS"
    assert p_elec["grace_period_days"] == 14

    p_mob = load_policy("mobile_phones")
    assert p_mob["category_code"] == "MOBILE_PHONES"
    assert p_mob["grace_period_days"] == 7

    p_app = load_policy("home_appliances")
    assert p_app["category_code"] == "HOME_APPLIANCES"
    assert p_app["grace_period_days"] == 30


def test_unauthorized_repairs_trigger_rejection(rule_engine):
    """Verify unauthorized repairs are rejected."""
    claim = {
        "product_category": "electronics",
        "remaining_warranty_days": 100,
        "warranty_active": "yes",
        "repair_history_count": 1,
        "repair_authorized": "unauthorized",
        "covered_fault": "yes",
        "damage_type": "internal_defect",
    }
    res = rule_engine.evaluate(claim)
    assert res["decision"] == DecisionType.REJECT.value
    assert any("UNAUTHORIZED_REPAIR" in v for v in res["violations"])


def test_late_reporting_triggers_rejection_or_review(rule_engine):
    """Verify claims reported far beyond deadline trigger violation."""
    claim = {
        "product_category": "electronics",
        "remaining_warranty_days": 100,
        "warranty_active": "yes",
        "claim_reporting_days": 60,
        "within_reporting_period": "no",
        "covered_fault": "yes",
    }
    res = rule_engine.evaluate(claim)
    assert res["decision"] in (DecisionType.REJECT.value, DecisionType.MANUAL_REVIEW.value)



def test_electronics_policy_structure_and_limits():
    """Verify Electronics policy configuration, allowed faults, exclusions, and repair limits."""
    policy = load_policy("electronics")
    assert policy["category_code"] == "ELECTRONICS"
    assert policy["grace_period_days"] == 14
    
    limits = policy["repair_limits"]
    assert limits["max_repair_cost_percentage"] == 75.0
    assert limits["max_claims_per_warranty"] == 3
    assert limits["total_aggregate_limit_percentage"] == 100.0
    assert limits["replacement_threshold_percentage"] == 80.0

    fault_codes = [f["code"] for f in policy["allowed_fault_types"]]
    assert "POWER_FAILURE" in fault_codes
    assert "DISPLAY_DEFECT" in fault_codes
    assert "AUDIO_FAILURE" in fault_codes
    assert "PORT_DEFECT" in fault_codes
    assert "FIRMWARE_CORRUPTION" in fault_codes

    exclusion_codes = [e["code"] for e in policy["exclusions"]]
    assert "PHYSICAL_IMPACT" in exclusion_codes
    assert "LIQUID_DAMAGE" in exclusion_codes
    assert "UNAUTHORIZED_MODIFICATION" in exclusion_codes
    assert "POWER_SURGE_UNPROTECTED" in exclusion_codes
    assert "NORMAL_WEAR_COSMETIC" in exclusion_codes


def test_home_appliances_policy_structure_and_limits():
    """Verify Home Appliances policy configuration, allowed faults, exclusions, and repair limits."""
    policy = load_policy("home_appliances")
    assert policy["category_code"] == "HOME_APPLIANCES"
    assert policy["grace_period_days"] == 30

    limits = policy["repair_limits"]
    assert limits["max_repair_cost_percentage"] == 70.0
    assert limits["max_claims_per_warranty"] == 4
    assert limits["total_aggregate_limit_percentage"] == 120.0
    assert limits["replacement_threshold_percentage"] == 75.0

    assert "installation_certificate" in policy["mandatory_documents"]

    fault_codes = [f["code"] for f in policy["allowed_fault_types"]]
    assert "COMPRESSOR_FAILURE" in fault_codes
    assert "MOTOR_FAILURE" in fault_codes
    assert "HEATING_ELEMENT_DEFECT" in fault_codes
    assert "CONTROL_BOARD_ERROR" in fault_codes
    assert "PUMP_LEAKAGE_INTERNAL" in fault_codes

    exclusion_codes = [e["code"] for e in policy["exclusions"]]
    assert "IMPROPER_INSTALLATION" in exclusion_codes
    assert "COMMERCIAL_USE" in exclusion_codes
    assert "PEST_INFESTATION" in exclusion_codes
    assert "FOREIGN_OBJECT_BLOCKAGE" in exclusion_codes


def test_mobile_phones_policy_structure_and_limits():
    """Verify Mobile Phones policy configuration, allowed faults, exclusions, and repair limits."""
    policy = load_policy("mobile_phones")
    assert policy["category_code"] == "MOBILE_PHONES"
    assert policy["grace_period_days"] == 7

    limits = policy["repair_limits"]
    assert limits["max_repair_cost_percentage"] == 65.0
    assert limits["max_claims_per_warranty"] == 2
    assert limits["total_aggregate_limit_percentage"] == 100.0
    assert limits["replacement_threshold_percentage"] == 70.0

    fault_codes = [f["code"] for f in policy["allowed_fault_types"]]
    assert "TOUCH_CONTROLLER_FAILURE" in fault_codes
    assert "BATTERY_DEGRADATION_PREMATURE" in fault_codes
    assert "CAMERA_MODULE_DEFECT" in fault_codes
    assert "NETWORK_BASEBAND_FAILURE" in fault_codes
    assert "CHARGING_IC_FAILURE" in fault_codes

    exclusion_codes = [e["code"] for e in policy["exclusions"]]
    assert "SCREEN_CRACK_ACCIDENTAL" in exclusion_codes
    assert "WATER_INGRESS_SUBMERSION" in exclusion_codes
    assert "UNAUTHORIZED_BATTERY_REPLACEMENT" in exclusion_codes
    assert "BENT_FRAME_STRUCTURAL" in exclusion_codes
    assert "STOLEN_OR_LOST" in exclusion_codes


def test_policy_grace_period_evaluation(rule_engine):
    """Verify grace period rules for various product categories."""
    res_elec_grace = rule_engine.evaluate({
        "product_category": "electronics",
        "warranty_active": "no",
        "remaining_warranty_days": -10,  # within 14 days grace
        "covered_fault": "yes",
    })
    assert res_elec_grace["decision"] == DecisionType.MANUAL_REVIEW.value
    assert any("GRACE_PERIOD" in w for w in res_elec_grace["warnings"])

    res_mob_expired = rule_engine.evaluate({
        "product_category": "mobile_phones",
        "warranty_active": "no",
        "remaining_warranty_days": -10,  # exceeds 7 days grace
        "covered_fault": "yes",
    })
    assert res_mob_expired["decision"] == DecisionType.REJECT.value
    assert any("POLICY_EXPIRED_WARRANTY" in v for v in res_mob_expired["violations"])

    res_app_grace = rule_engine.evaluate({
        "product_category": "home_appliances",
        "warranty_active": "no",
        "remaining_warranty_days": -20,  # within 30 days grace
        "covered_fault": "yes",
    })
    assert res_app_grace["decision"] == DecisionType.MANUAL_REVIEW.value
    assert any("GRACE_PERIOD" in w for w in res_app_grace["warnings"])


def test_specific_category_damage_exclusions(rule_engine):
    """Verify category-specific damage exclusions like Screen Crack on mobile, Improper Installation on appliances."""
    res_mobile_crack = rule_engine.evaluate({
        "product_category": "mobile_phones",
        "damage_type": "screen_crack_accidental",
        "remaining_warranty_days": 180,
    })
    assert res_mobile_crack["decision"] == DecisionType.REJECT.value
    assert any("POLICY_EXCLUDED_DAMAGE" in v for v in res_mobile_crack["violations"])

    res_app_install = rule_engine.evaluate({
        "product_category": "home_appliances",
        "damage_type": "improper_installation",
        "remaining_warranty_days": 200,
    })
    assert res_app_install["decision"] == DecisionType.REJECT.value
    assert any("POLICY_EXCLUDED_DAMAGE" in v for v in res_app_install["violations"])

    res_surge = rule_engine.evaluate({
        "product_category": "electronics",
        "damage_type": "power_surge_unprotected",
        "remaining_warranty_days": 100,
    })
    assert res_surge["decision"] == DecisionType.MANUAL_REVIEW.value
    assert any("POLICY_EXCLUSION_REVIEW" in w for w in res_surge["warnings"])