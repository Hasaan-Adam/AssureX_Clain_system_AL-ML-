"""Unit tests for Model Disagreement and Fallback Handling."""

import pytest
from src.services.comparison_service import ComparisonService, compare_models
from src.utils.constants import DecisionType


def test_models_concordance():
    """All models agree on APPROVE."""
    ml_pred = {"decision": DecisionType.APPROVE.value, "confidence": 0.90}
    rule_pred = {"decision": DecisionType.APPROVE.value, "passed": True}
    res = compare_models(ml_pred, rule_pred)
    assert res["agreement"] is True
    assert res["agreement_score"] == 1.0
    assert res["consensus_decision"] == DecisionType.APPROVE.value


def test_models_disagreement():
    """ML predicts APPROVE while Rule Engine predicts REJECT -> Routes to MANUAL_REVIEW."""
    ml_pred = {"decision": DecisionType.APPROVE.value, "confidence": 0.90}
    rule_pred = {"decision": DecisionType.REJECT.value, "passed": False}
    res = compare_models(ml_pred, rule_pred)
    assert res["agreement"] is False
    assert res["consensus_decision"] == DecisionType.MANUAL_REVIEW.value
    assert res["discrepancy_details"] is not None


def test_dual_ai_strong_match():
    """Python ML and TM vision predictions within 0.10 delta -> Strong Match."""
    py_pred = {
        "predicted_class": "Valid Claim",
        "confidence": 0.92,
        "probabilities": {"Valid Claim": 0.92, "Invalid Claim": 0.05, "Manual Review": 0.03},
    }
    tm_pred = {
        "predicted_class": "Valid Claim",
        "confidence": 0.89,
        "probabilities": {"Valid Claim": 0.89, "Invalid Claim": 0.06, "Manual Review": 0.05},
    }
    res = compare_models(py_pred, tm_prediction=tm_pred)
    assert res["consistency_status"] == "Strong Match"
    assert res["max_delta"] <= 0.10
    assert res["requires_manual_review"] is False


def test_dual_ai_disagreement_delta():
    """Different top class -> Disagreement status."""
    py_pred = {
        "predicted_class": "Valid Claim",
        "confidence": 0.85,
        "probabilities": {"Valid Claim": 0.85, "Invalid Claim": 0.10, "Manual Review": 0.05},
    }
    tm_pred = {
        "predicted_class": "Invalid Claim",
        "confidence": 0.82,
        "probabilities": {"Valid Claim": 0.10, "Invalid Claim": 0.82, "Manual Review": 0.08},
    }
    res = compare_models(py_pred, tm_prediction=tm_pred)
    assert res["consistency_status"] == "Disagreement"
    assert res["requires_manual_review"] is True
    assert res["consensus_decision"] == DecisionType.MANUAL_REVIEW.value


def test_dual_ai_acceptable_match():
    """Variance between 0.10 and 0.20 delta -> Acceptable status."""
    py_pred = {
        "predicted_class": "Valid Claim",
        "confidence": 0.90,
        "probabilities": {"Valid Claim": 0.90, "Invalid Claim": 0.06, "Manual Review": 0.04},
    }
    tm_pred = {
        "predicted_class": "Valid Claim",
        "confidence": 0.75,
        "probabilities": {"Valid Claim": 0.75, "Invalid Claim": 0.18, "Manual Review": 0.07},
    }
    res = compare_models(py_pred, tm_prediction=tm_pred)
    assert res["consistency_status"] == "Acceptable"
    assert 0.10 < res["max_delta"] <= 0.20
    assert res["requires_manual_review"] is False
    assert res["agreement"] is True


def test_dual_ai_weak_match():
    """Variance between 0.20 and 0.35 delta -> Weak status triggering review."""
    py_pred = {
        "predicted_class": "Valid Claim",
        "confidence": 0.90,
        "probabilities": {"Valid Claim": 0.90, "Invalid Claim": 0.06, "Manual Review": 0.04},
    }
    tm_pred = {
        "predicted_class": "Valid Claim",
        "confidence": 0.65,
        "probabilities": {"Valid Claim": 0.65, "Invalid Claim": 0.25, "Manual Review": 0.10},
    }
    res = compare_models(py_pred, tm_prediction=tm_pred)
    assert res["consistency_status"] == "Weak"
    assert 0.20 < res["max_delta"] <= 0.35
    assert res["requires_manual_review"] is True
    assert res["consensus_decision"] == DecisionType.MANUAL_REVIEW.value


def test_dual_ai_uncertain_low_confidence():
    """Both models below low confidence threshold (< 0.60) -> Uncertain status."""
    py_pred = {
        "predicted_class": "Valid Claim",
        "confidence": 0.52,
        "probabilities": {"Valid Claim": 0.52, "Invalid Claim": 0.40, "Manual Review": 0.08},
    }
    tm_pred = {
        "predicted_class": "Valid Claim",
        "confidence": 0.55,
        "probabilities": {"Valid Claim": 0.55, "Invalid Claim": 0.38, "Manual Review": 0.07},
    }
    res = compare_models(py_pred, tm_prediction=tm_pred)
    assert res["consistency_status"] == "Uncertain"
    assert res["requires_manual_review"] is True
    assert res["consensus_decision"] == DecisionType.MANUAL_REVIEW.value


def test_delta_calculation_exact():
    """Verify $|P_{py} - P_{tm}|$ delta calculations across all probability classes."""
    py_pred = {
        "predicted_class": "Valid Claim",
        "confidence": 0.80,
        "probabilities": {"Valid Claim": 0.80, "Invalid Claim": 0.15, "Manual Review": 0.05},
    }
    tm_pred = {
        "predicted_class": "Valid Claim",
        "confidence": 0.70,
        "probabilities": {"Valid Claim": 0.70, "Invalid Claim": 0.22, "Manual Review": 0.08},
    }
    res = compare_models(py_pred, tm_prediction=tm_pred)
    # Deltas: Valid Claim = |0.80 - 0.70| = 0.10
    # Invalid Claim = |0.15 - 0.22| = 0.07
    # Manual Review = |0.05 - 0.08| = 0.03
    assert res["deltas"]["Valid Claim"] == pytest.approx(0.10, rel=1e-3)
    assert res["deltas"]["Invalid Claim"] == pytest.approx(0.07, rel=1e-3)
    assert res["deltas"]["Manual Review"] == pytest.approx(0.03, rel=1e-3)
    assert res["max_delta"] == pytest.approx(0.10, rel=1e-3)
    assert res["consistency_status"] == "Strong Match"