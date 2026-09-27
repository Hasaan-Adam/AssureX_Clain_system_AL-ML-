"""AssureX Claim Engine - Python Machine Learning Pipeline.

Exports core feature engineering, preprocessing, training, evaluation, and prediction interfaces.
"""

from src.ml.evaluate import evaluate_model
from src.ml.feature_engineering import extract_features, extract_features_and_target
from src.ml.predict import ClaimPredictor, batch_predict_claims, predict_claim
from src.ml.preprocess_pipeline import (
    build_label_encoder,
    build_preprocessor,
    load_label_encoder,
    load_preprocessor,
)
from src.ml.registry import get_latest_version, register_model_version
from src.ml.train import train_and_evaluate_models


__all__ = [
    "extract_features",
    "extract_features_and_target",
    "build_preprocessor",
    "build_label_encoder",
    "load_preprocessor",
    "load_label_encoder",
    "train_and_evaluate_models",
    "evaluate_model",
    "predict_claim",
    "batch_predict_claims",
    "ClaimPredictor",
    "register_model_version",
    "get_latest_version",
]