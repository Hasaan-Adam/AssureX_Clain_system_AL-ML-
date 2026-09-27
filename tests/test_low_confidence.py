"""
Unit tests for Low Confidence Claim Routing.
"""

import pytest
from src.services.prediction_service import calculate_fraud_risk
from src.services.decision_service import aggregate_decision
from src.utils.constants import DecisionType


def test_low_confidence_triggers_review():
    """Confidence below 0.80 routes to MANUAL_REVIEW."""
    res = aggregate_decision(ml_confidence=0.65, fraud_score=0.10, rule_passed=True)
    assert res["decision"] == DecisionType.MANUAL_REVIEW.value


def test_elevated_risk_triggers_review():
    """Fraud score >= 0.30 routes to MANUAL_REVIEW."""
    res = aggregate_decision(ml_confidence=0.90, fraud_score=0.45, rule_passed=True)
    assert res["decision"] == DecisionType.MANUAL_REVIEW.value