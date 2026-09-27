"""Unit tests for ML Algorithm Comparison and Selection."""

from pathlib import Path
import pytest

from src.ml.train import get_candidate_models, train_and_evaluate_models


def test_candidate_models_definition():
    """Verify at least 3 distinct algorithms are configured for benchmarking."""
    candidates = get_candidate_models()
    assert len(candidates) >= 3
    assert "RandomForest" in candidates or "XGBoost" in candidates or "LogisticRegression" in candidates


def test_train_and_benchmark_execution(tmp_path):
    """Verify model training and selection pipeline executes cleanly."""
    model_out = tmp_path / "claim_classifier.joblib"
    best_model, benchmark_results, reg_entry = train_and_evaluate_models(
        train_csv=Path("data/train/claims_train.csv"),
        val_csv=Path("data/validation/claims_validation.csv"),
        model_output_path=model_out,
        version="v1.0.0-test",
    )

    assert best_model is not None
    assert model_out.exists()
    assert len(benchmark_results) >= 3
    for name, res in benchmark_results.items():
        assert "train_accuracy" in res
        assert "val_accuracy" in res
        assert "val_f1_macro" in res
        assert res["val_accuracy"] >= 0.85