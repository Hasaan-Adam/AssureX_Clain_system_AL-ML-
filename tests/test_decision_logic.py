"""Unit tests for Decision Aggregation and Adjudication Logic."""

import os
from pathlib import Path
from PIL import Image
import pytest

from src.services.ai_summary_service import (
    generate_claim_executive_summary,
    generate_claim_narrative,
)
from src.services.decision_service import DecisionService, adjudicate_claim, aggregate_decision
from src.services.explanation_service import (
    format_explanation_markdown,
    generate_claim_explanation,
)
from src.services.model_version_service import (
    get_active_version,
    get_version_metadata,
    list_model_versions,
)
from src.services.prediction_service import predict_tabular_claim
from src.services.prep_assist_service import assess_claim_readiness
from src.services.summary_card_service import (
    generate_summary_card,
    generate_summary_card_base64,
    render_summary_card_image,
)
from src.services.tm_service import predict_claim_card
from src.utils.constants import DecisionType


def test_aggregate_decision_approve():
    """High confidence, low fraud, rule passed -> APPROVE."""
    res = aggregate_decision(ml_confidence=0.92, fraud_score=0.05, rule_passed=True)
    assert res["decision"] == DecisionType.APPROVE.value


def test_aggregate_decision_rule_failed():
    """Rule failure -> REJECT."""
    res = aggregate_decision(ml_confidence=0.95, fraud_score=0.05, rule_passed=False)
    assert res["decision"] == DecisionType.REJECT.value


def test_aggregate_decision_high_fraud():
    """Fraud score >= 0.70 -> REJECT."""
    res = aggregate_decision(ml_confidence=0.90, fraud_score=0.75, rule_passed=True)
    assert res["decision"] == DecisionType.REJECT.value


def test_aggregate_decision_manual_review():
    """Medium fraud or lower confidence -> MANUAL_REVIEW."""
    res = aggregate_decision(ml_confidence=0.70, fraud_score=0.35, rule_passed=True)
    assert res["decision"] == DecisionType.MANUAL_REVIEW.value


def test_adjudicate_valid_claim_full_pipeline(sample_valid_claim_dict):
    """End-to-end full claim adjudication on clean claim."""
    res = adjudicate_claim(sample_valid_claim_dict)
    assert res["final_decision"] == "Valid Claim"
    assert res["confidence"] >= 0.70
    assert res["requires_human_review"] is False


def test_adjudicate_invalid_claim_on_exclusion(sample_valid_claim_dict):
    """Excluded damage results in Invalid Claim."""
    claim = sample_valid_claim_dict.copy()
    claim["damage_type"] = "PHYSICAL_IMPACT"
    claim["excluded_damage"] = "yes"
    res = adjudicate_claim(claim)
    assert res["final_decision"] == "Invalid Claim"


def test_explanation_generation(sample_valid_claim_dict):
    """Generate human-readable transparent explanation."""
    adj_res = adjudicate_claim(sample_valid_claim_dict)
    exp = generate_claim_explanation(adj_res, claim_data=sample_valid_claim_dict)
    assert exp["decision"] == "Valid Claim"
    assert len(exp["supporting_factors"]) > 0

    md = format_explanation_markdown(exp)
    assert "# AssureX Claim Adjudication Explanation" in md


def test_prep_assist_readiness(sample_valid_claim_dict):
    """Evaluate pre-submission claim readiness score."""
    readiness = assess_claim_readiness(sample_valid_claim_dict)
    assert readiness["is_ready"] is True
    assert readiness["readiness_score"] >= 75


def test_summary_card_generation(sample_valid_claim_dict, tmp_path):
    """Verify live rendering and saving of Claim Summary Card."""
    img = render_summary_card_image(sample_valid_claim_dict)
    assert isinstance(img, Image.Image)

    b64 = generate_summary_card_base64(sample_valid_claim_dict)
    assert b64.startswith("data:image/png;base64,")

    out_file = tmp_path / "summary_card.png"
    saved = generate_summary_card(sample_valid_claim_dict, output_path=out_file)
    assert Path(saved).exists()


def test_model_version_service():
    """Verify active model version retrieval."""
    ver = get_active_version()
    assert ver.startswith("v")
    meta = get_version_metadata()
    assert meta["version"] == ver
    versions = list_model_versions()
    assert len(versions) >= 1