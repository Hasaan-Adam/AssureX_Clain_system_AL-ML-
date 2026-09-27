"""Model Evaluation Pipeline for AssureX Claim Engine.

Evaluates the deployed/trained model artifacts against the held-out test split (or custom dataset).
Computes comprehensive multi-class evaluation metrics, confusion matrix, per-class breakdown,
and verifies SRS requirement compliance (Test Accuracy >= 85%).
"""

from __future__ import annotations

import argparse
import json
import logging
import os
from pathlib import Path
import sys
from typing import Any, Dict, Optional, Union

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

from src.ml.feature_engineering import TARGET_COLUMN, extract_features_and_target
from src.ml.preprocess_pipeline import (
    DEFAULT_LABEL_ENCODER_PATH,
    DEFAULT_PREPROCESSOR_PATH,
    load_label_encoder,
    load_preprocessor,
)
from src.ml.registry import get_latest_version, register_model_version, update_model_card


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_TEST_PATH = Path("data/test/claims_test.csv")
DEFAULT_MODEL_PATH = Path("model/python/claim_classifier.joblib")
DEFAULT_REPORT_PATH = Path("model/python/evaluation_report.json")


def evaluate_model(
    test_csv: Union[str, Path] = DEFAULT_TEST_PATH,
    model_path: Union[str, Path] = DEFAULT_MODEL_PATH,
    preprocessor_path: Union[str, Path] = DEFAULT_PREPROCESSOR_PATH,
    label_encoder_path: Union[str, Path] = DEFAULT_LABEL_ENCODER_PATH,
    report_output_path: Union[str, Path] = DEFAULT_REPORT_PATH,
) -> Dict[str, Any]:
    """Runs rigorous multi-class evaluation on the test dataset.
    
    Args:
        test_csv: Path to test dataset CSV.
        model_path: Path to serialized trained model artifact.
        preprocessor_path: Path to serialized preprocessor.
        label_encoder_path: Path to serialized label encoder.
        report_output_path: Path to save output JSON evaluation report.
        
    Returns:
        Dictionary with full evaluation metrics, per-class stats, and confusion matrix.
    """
    logger.info(f"Loading test dataset from: {test_csv}")
    test_df = pd.read_csv(test_csv)

    logger.info(f"Loading model artifacts from {model_path}, {preprocessor_path}, {label_encoder_path}...")
    model = joblib.load(model_path)
    preprocessor = load_preprocessor(preprocessor_path)
    label_encoder = load_label_encoder(label_encoder_path)

    # 1. Feature Extraction & Transform
    X_test, y_test = extract_features_and_target(test_df, TARGET_COLUMN)
    X_test_trans = preprocessor.transform(X_test)
    y_test_enc = label_encoder.transform(y_test)
    class_names = list(label_encoder.classes_)

    # 2. Prediction & Probabilities
    y_pred_enc = model.predict(X_test_trans)
    y_pred = label_encoder.inverse_transform(y_pred_enc)

    # 3. Overall Metrics Calculation
    acc = accuracy_score(y_test_enc, y_pred_enc)
    prec_macro = precision_score(y_test_enc, y_pred_enc, average="macro", zero_division=0)
    prec_weighted = precision_score(y_test_enc, y_pred_enc, average="weighted", zero_division=0)
    rec_macro = recall_score(y_test_enc, y_pred_enc, average="macro", zero_division=0)
    rec_weighted = recall_score(y_test_enc, y_pred_enc, average="weighted", zero_division=0)
    f1_macro = f1_score(y_test_enc, y_pred_enc, average="macro", zero_division=0)
    f1_weighted = f1_score(y_test_enc, y_pred_enc, average="weighted", zero_division=0)

    cm = confusion_matrix(y_test_enc, y_pred_enc)
    clf_dict = classification_report(y_test_enc, y_pred_enc, target_names=class_names, output_dict=True)

    # 4. Class-wise Breakdown
    class_breakdown = {}
    for idx, cname in enumerate(class_names):
        class_breakdown[cname] = {
            "precision": float(clf_dict[cname]["precision"]),
            "recall": float(clf_dict[cname]["recall"]),
            "f1-score": float(clf_dict[cname]["f1-score"]),
            "support": int(clf_dict[cname]["support"]),
        }

    srs_met = bool(acc >= 0.85)

    evaluation_report = {
        "test_dataset": str(test_csv),
        "total_test_samples": int(len(test_df)),
        "srs_requirement_met": srs_met,
        "metrics": {
            "accuracy": float(acc),
            "precision_macro": float(prec_macro),
            "precision_weighted": float(prec_weighted),
            "recall_macro": float(rec_macro),
            "recall_weighted": float(rec_weighted),
            "f1_macro": float(f1_macro),
            "f1_weighted": float(f1_weighted),
        },
        "classes": class_names,
        "class_breakdown": class_breakdown,
        "confusion_matrix": cm.tolist(),
    }

    # Format human-readable output
    report_text = f"""
================================================================================
                    ASSUREX CLAIM ENGINE — MODEL EVALUATION
================================================================================
Test Dataset:            {test_csv}
Total Test Samples:      {len(test_df)}
Accuracy:                {acc * 100:.2f}% (SRS Target: >= 85.00%)
SRS Requirement Met:     {'PASSED (>= 85%)' if srs_met else 'FAILED (< 85%)'}
Macro Precision:         {prec_macro:.4f}
Macro Recall:            {rec_macro:.4f}
Macro F1-Score:          {f1_macro:.4f}
Weighted F1-Score:       {f1_weighted:.4f}

--------------------------------------------------------------------------------
                              CLASS-WISE METRICS
--------------------------------------------------------------------------------
{f"{'Class':<20} | {'Precision':<10} | {'Recall':<10} | {'F1-Score':<10} | {'Support':<8}"}
{"-" * 68}"""
    for cname, metrics_dict in class_breakdown.items():
        report_text += f"\n{cname:<20} | {metrics_dict['precision']:<10.4f} | {metrics_dict['recall']:<10.4f} | {metrics_dict['f1-score']:<10.4f} | {metrics_dict['support']:<8d}"

    report_text += f"""
--------------------------------------------------------------------------------
                              CONFUSION MATRIX
--------------------------------------------------------------------------------
Labels order: {class_names}
{cm}
================================================================================
"""
    logger.info(report_text)

    # 5. Persist Evaluation Report
    report_path_obj = Path(report_output_path)
    report_path_obj.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path_obj, "w", encoding="utf-8") as f:
        json.dump(evaluation_report, f, indent=2)
    logger.info(f"Saved evaluation report to: {report_path_obj.resolve()}")

    # 6. Update Registry with Test Metrics
    latest_entry = get_latest_version()
    if latest_entry:
        latest_entry["metrics"]["test_accuracy"] = float(acc)
        latest_entry["metrics"]["test_precision_macro"] = float(prec_macro)
        latest_entry["metrics"]["test_recall_macro"] = float(rec_macro)
        latest_entry["metrics"]["test_f1_macro"] = float(f1_macro)
        latest_entry["metrics"]["test_f1_weighted"] = float(f1_weighted)
        
        reg_entry = register_model_version(
            version=latest_entry.get("version", "v1.0.0"),
            algorithm=latest_entry.get("algorithm", "Unknown"),
            hyperparameters=latest_entry.get("hyperparameters", {}),
            metrics=latest_entry["metrics"],
            framework=latest_entry.get("framework", "scikit-learn / xgboost"),
            description=latest_entry.get("description", "Automated warranty claim classifier"),
        )
        update_model_card(reg_entry)

    return evaluation_report


def main():
    parser = argparse.ArgumentParser(description="Evaluate ML model for AssureX Claim Engine.")
    parser.add_argument("--test-data", type=str, default=str(DEFAULT_TEST_PATH), help="Path to test CSV.")
    parser.add_argument("--model-path", type=str, default=str(DEFAULT_MODEL_PATH), help="Path to model artifact.")
    parser.add_argument("--report-output", type=str, default=str(DEFAULT_REPORT_PATH), help="Path to output JSON.")

    args = parser.parse_args()
    evaluate_model(
        test_csv=Path(args.test_data),
        model_path=Path(args.model_path),
        report_output_path=Path(args.report_output),
    )


if __name__ == "__main__":
    main()