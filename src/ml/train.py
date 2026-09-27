"""Model Training and Algorithm Selection Pipeline for AssureX Claim Engine.

Trains and benchmarks multiple machine learning algorithms on training claims data,
evaluates on validation data, selects the optimal classifier exceeding the SRS accuracy
requirement (>= 85%), and exports serialized artifacts and metadata.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Tuple

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score
from xgboost import XGBClassifier

from src.ml.feature_engineering import (
    BOOLEAN_FEATURES,
    CATEGORICAL_FEATURES,
    FEATURE_COLUMNS,
    NUMERIC_FEATURES,
    TARGET_COLUMN,
    extract_features_and_target,
)
from src.ml.preprocess_pipeline import (
    DEFAULT_LABEL_ENCODER_PATH,
    DEFAULT_PREPROCESSOR_PATH,
    fit_and_save_pipeline,
)
from src.ml.registry import register_model_version, update_model_card


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_TRAIN_PATH = Path("data/train/claims_train.csv")
DEFAULT_VAL_PATH = Path("data/validation/claims_validation.csv")
DEFAULT_MODEL_PATH = Path("model/python/claim_classifier.joblib")
DEFAULT_FEATURES_PATH = Path("model/python/feature_columns.json")


def save_feature_columns_metadata(
    classes: List[str],
    path: Path = DEFAULT_FEATURES_PATH,
) -> Path:
    """Saves feature column lists and target classes to JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    metadata = {
        "feature_columns": FEATURE_COLUMNS,
        "numeric_features": NUMERIC_FEATURES,
        "boolean_features": BOOLEAN_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "target_column": TARGET_COLUMN,
        "classes": sorted(list(classes)),
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    return path


def get_candidate_models() -> Dict[str, Any]:
    """Returns candidate classification algorithms with tuned hyperparameters."""
    return {
        "XGBoost": XGBClassifier(
            n_estimators=150,
            max_depth=6,
            learning_rate=0.08,
            subsample=0.9,
            colsample_bytree=0.9,
            random_state=42,
            eval_metric="mlogloss",
        ),
        "RandomForest": RandomForestClassifier(
            n_estimators=150,
            max_depth=12,
            min_samples_split=4,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,
        ),
        "HistGradientBoosting": HistGradientBoostingClassifier(
            max_iter=150,
            learning_rate=0.08,
            max_depth=8,
            random_state=42,
        ),
        "LogisticRegression": LogisticRegression(
            C=1.0,
            max_iter=1000,
            random_state=42,
            solver="lbfgs",
        ),
    }


def train_and_evaluate_models(
    train_csv: Path = DEFAULT_TRAIN_PATH,
    val_csv: Path = DEFAULT_VAL_PATH,
    model_output_path: Path = DEFAULT_MODEL_PATH,
    version: str = "v1.0.0",
) -> Tuple[Any, Dict[str, Any], Dict[str, Any]]:
    """Trains candidate algorithms, evaluates on validation data, and persists best model.
    
    Returns:
        Tuple of (best_model, benchmark_results, best_model_info).
    """
    logger.info(f"Loading training data from: {train_csv}")
    train_df = pd.read_csv(train_csv)
    logger.info(f"Loading validation data from: {val_csv}")
    val_df = pd.read_csv(val_csv)

    # 1. Feature Engineering
    logger.info("Extracting features from train and validation sets...")
    X_train, y_train = extract_features_and_target(train_df, TARGET_COLUMN)
    X_val, y_val = extract_features_and_target(val_df, TARGET_COLUMN)

    # 2. Preprocessing Pipeline (Fit & Save)
    logger.info("Fitting and saving preprocessor and label encoder...")
    preprocessor, label_encoder, X_train_trans, y_train_enc = fit_and_save_pipeline(
        X_train, y_train, DEFAULT_PREPROCESSOR_PATH, DEFAULT_LABEL_ENCODER_PATH
    )
    X_val_trans = preprocessor.transform(X_val)
    y_val_enc = label_encoder.transform(y_val)

    classes_list = list(label_encoder.classes_)
    save_feature_columns_metadata(classes_list, DEFAULT_FEATURES_PATH)
    logger.info(f"Label classes: {classes_list}")

    # 3. Model Training & Benchmarking
    candidate_models = get_candidate_models()
    benchmark_results: Dict[str, Dict[str, Any]] = {}
    best_name = None
    best_val_f1 = -1.0
    best_model = None

    logger.info("--- Starting Model Benchmarking ---")
    for name, model in candidate_models.items():
        logger.info(f"Training algorithm: {name}...")
        model.fit(X_train_trans, y_train_enc)

        # Train metrics
        train_preds = model.predict(X_train_trans)
        train_acc = accuracy_score(y_train_enc, train_preds)
        train_f1 = f1_score(y_train_enc, train_preds, average="macro")

        # Validation metrics
        val_preds = model.predict(X_val_trans)
        val_acc = accuracy_score(y_val_enc, val_preds)
        val_f1 = f1_score(y_val_enc, val_preds, average="macro")
        val_f1_weighted = f1_score(y_val_enc, val_preds, average="weighted")

        benchmark_results[name] = {
            "train_accuracy": float(train_acc),
            "train_f1_macro": float(train_f1),
            "val_accuracy": float(val_acc),
            "val_f1_macro": float(val_f1),
            "val_f1_weighted": float(val_f1_weighted),
            "hyperparameters": model.get_params() if hasattr(model, "get_params") else {},
        }

        logger.info(
            f"Algorithm {name:20s} | Val Acc: {val_acc * 100:.2f}% | Val F1 (macro): {val_f1:.4f} | Val F1 (weighted): {val_f1_weighted:.4f}"
        )

        # Selection criterion: Highest Validation F1 / Accuracy
        if val_f1 > best_val_f1:
            best_val_f1 = val_f1
            best_name = name
            best_model = model

    logger.info(f"--- Best Algorithm Selected: {best_name} (Validation F1: {best_val_f1:.4f}) ---")

    # Check SRS Requirement (>= 85% accuracy)
    best_val_acc = benchmark_results[best_name]["val_accuracy"]
    if best_val_acc < 0.85:
        raise RuntimeError(
            f"Best model {best_name} achieved {best_val_acc * 100:.2f}% accuracy, which fails the SRS >= 85% requirement!"
        )

    # 4. Save Best Model
    model_output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_model, model_output_path)
    logger.info(f"Saved best model artifact to: {model_output_path.resolve()}")

    # 5. Registry Entry & Model Card Update
    best_metrics = {
        "train_accuracy": benchmark_results[best_name]["train_accuracy"],
        "train_f1_macro": benchmark_results[best_name]["train_f1_macro"],
        "val_accuracy": benchmark_results[best_name]["val_accuracy"],
        "val_f1_macro": benchmark_results[best_name]["val_f1_macro"],
        "val_f1_weighted": benchmark_results[best_name]["val_f1_weighted"],
    }

    reg_entry = register_model_version(
        version=version,
        algorithm=best_name,
        hyperparameters=benchmark_results[best_name]["hyperparameters"],
        metrics=best_metrics,
        framework="xgboost" if "XGB" in best_name else "scikit-learn",
        description=f"Automated warranty claim classifier trained using {best_name} algorithm.",
    )
    update_model_card(reg_entry)
    logger.info(f"Model version {version} registered and model card updated.")

    return best_model, benchmark_results, reg_entry


def main():
    parser = argparse.ArgumentParser(description="Train and evaluate ML models for AssureX Claim Engine.")
    parser.add_argument("--train-data", type=str, default=str(DEFAULT_TRAIN_PATH), help="Path to training CSV.")
    parser.add_argument("--val-data", type=str, default=str(DEFAULT_VAL_PATH), help="Path to validation CSV.")
    parser.add_argument("--model-output", type=str, default=str(DEFAULT_MODEL_PATH), help="Path to save best model.")
    parser.add_argument("--version", type=str, default="v1.0.0", help="Model version tag.")

    args = parser.parse_args()
    train_and_evaluate_models(
        train_csv=Path(args.train_data),
        val_csv=Path(args.val_data),
        model_output_path=Path(args.model_output),
        version=args.version,
    )


if __name__ == "__main__":
    main()