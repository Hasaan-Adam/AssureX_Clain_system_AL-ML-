"""Model Registry and Version Tracking Module for AssureX Claim Engine.

Maintains model metadata, version history, training metrics, and generates model cards.
Persists versions in `model/versions.json` and documents details in `model/python/model_card.md`.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


VERSIONS_FILE_PATH = Path("model/versions.json")
MODEL_CARD_PATH = Path("model/python/model_card.md")


def load_registry(versions_path: Union[str, Path] = VERSIONS_FILE_PATH) -> Dict[str, Any]:
    """Loads the model version registry JSON file. Returns empty structure if absent/invalid."""
    path = Path(versions_path)
    if not path.exists():
        return {"current_version": None, "models": []}
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content or content == "TODO":
                return {"current_version": None, "models": []}
            return json.loads(content)
    except Exception:
        return {"current_version": None, "models": []}


def save_registry(registry_data: Dict[str, Any], versions_path: Union[str, Path] = VERSIONS_FILE_PATH) -> Path:
    """Saves the version registry dictionary to JSON."""
    path = Path(versions_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(registry_data, f, indent=2)
    return path


def register_model_version(
    version: str,
    algorithm: str,
    hyperparameters: Dict[str, Any],
    metrics: Dict[str, Any],
    artifacts: Optional[Dict[str, str]] = None,
    framework: str = "scikit-learn / xgboost",
    description: str = "Automated warranty claim classification model",
    versions_path: Union[str, Path] = VERSIONS_FILE_PATH,
) -> Dict[str, Any]:
    """Registers a new model version entry in model/versions.json.
    
    Args:
        version: Semantic version string (e.g. 'v1.0.0').
        algorithm: Algorithm name (e.g. 'XGBClassifier', 'RandomForestClassifier').
        hyperparameters: Dictionary of training hyperparameters.
        metrics: Dictionary of evaluation metrics (train_accuracy, val_accuracy, test_accuracy, f1, etc.).
        artifacts: Paths to saved artifact files.
        framework: ML framework used.
        description: Description of the model release.
        versions_path: Path to versions.json file.
        
    Returns:
        The newly created model entry dict.
    """
    registry = load_registry(versions_path)
    
    # Ensure artifacts dictionary
    if artifacts is None:
        artifacts = {
            "model_path": "model/python/claim_classifier.joblib",
            "preprocessor_path": "model/python/preprocessor.joblib",
            "label_encoder_path": "model/python/label_encoder.joblib",
            "feature_columns_path": "model/python/feature_columns.json",
        }

    # Clean serializable hyperparameters
    clean_params = {}
    for k, v in hyperparameters.items():
        if isinstance(v, (int, float, str, bool, list, dict)) or v is None:
            clean_params[k] = v
        else:
            clean_params[k] = str(v)

    # SRS Requirement Check (Test/Val Accuracy >= 85%)
    test_acc = metrics.get("test_accuracy", metrics.get("val_accuracy", 0.0))
    srs_met = bool(test_acc >= 0.85)

    entry: Dict[str, Any] = {
        "version": version,
        "algorithm": algorithm,
        "framework": framework,
        "registered_at": datetime.now(timezone.utc).isoformat(),
        "status": "active",
        "description": description,
        "srs_requirement_met": srs_met,
        "hyperparameters": clean_params,
        "metrics": metrics,
        "artifacts": artifacts,
    }

    # Update models list (mark previous ones archived if needed or keep history)
    existing_models = registry.get("models", [])
    updated_models = []
    found = False
    for m in existing_models:
        if m.get("version") == version:
            updated_models.append(entry)
            found = True
        else:
            m["status"] = "archived"
            updated_models.append(m)
            
    if not found:
        updated_models.append(entry)

    registry["current_version"] = version
    registry["models"] = updated_models
    registry["last_updated"] = datetime.now(timezone.utc).isoformat()

    save_registry(registry, versions_path)
    return entry


def get_latest_version(versions_path: Union[str, Path] = VERSIONS_FILE_PATH) -> Optional[Dict[str, Any]]:
    """Returns the latest active model version entry from registry."""
    registry = load_registry(versions_path)
    models = registry.get("models", [])
    if not models:
        return None
    for m in reversed(models):
        if m.get("status") == "active":
            return m
    return models[-1]


def update_model_card(
    version_entry: Dict[str, Any],
    card_path: Union[str, Path] = MODEL_CARD_PATH,
) -> Path:
    """Generates and writes a comprehensive Markdown Model Card."""
    card_file = Path(card_path)
    card_file.parent.mkdir(parents=True, exist_ok=True)

    metrics = version_entry.get("metrics", {})
    params = version_entry.get("hyperparameters", {})

    content = f"""# Model Card: AssureX Claim Classifier ({version_entry.get('version', 'v1.0.0')})

## Model Overview
- **Model Name:** AssureX Claim Classifier
- **Model Version:** `{version_entry.get('version', 'v1.0.0')}`
- **Algorithm:** `{version_entry.get('algorithm', 'XGBClassifier')}`
- **Framework:** `{version_entry.get('framework', 'scikit-learn / xgboost')}`
- **Registration Date:** `{version_entry.get('registered_at', 'N/A')}`
- **Status:** `{version_entry.get('status', 'active')}`
- **SRS Requirement (>=85% Accuracy):** `{'PASSED' if version_entry.get('srs_requirement_met') else 'FAILED'}`

---

## Intended Use
The AssureX Claim Classifier is an automated ML model for warranty claim triage. It classifies warranty claims into three discrete operational buckets:
1. **Valid Claim:** Legitimate warranty claim with active coverage, genuine serial, valid documentation, and covered defect.
2. **Invalid Claim:** Fraudulent or out-of-warranty claim (e.g., expired warranty, excluded damage type, serial mismatch, duplicate submission).
3. **Manual Review:** Boundary, ambiguous, or incomplete claims requiring human inspection (e.g., grace period boundary, missing secondary documents, minor data discrepancies).

---

## Performance Summary

| Split | Metric | Value | Requirement |
|-------|--------|-------|-------------|
| Validation | Accuracy | {metrics.get('val_accuracy', 0.0) * 100:.2f}% | >= 85.00% |
| Validation | Macro F1 | {metrics.get('val_f1_macro', 0.0):.4f} | - |
| Test | Accuracy | {metrics.get('test_accuracy', 0.0) * 100:.2f}% | >= 85.00% |
| Test | Macro F1 | {metrics.get('test_f1_macro', 0.0):.4f} | - |
| Test | Weighted F1 | {metrics.get('test_f1_weighted', 0.0):.4f} | - |

---

## Hyperparameters
```json
{json.dumps(params, indent=2)}
```

---

## Feature Engineering & Preprocessing
- **Numeric Features Imputation & Scaling:** Median imputation + StandardScaler.
- **Categorical Features Encoding:** Missing constant imputation + OneHotEncoder (`handle_unknown='ignore'`).
- **Engineered Domain Features:**
  - `product_age_days`: Days between purchase and claim submission.
  - `remaining_warranty_days`: Days remaining before policy expiration (negative indicates expired).
  - `price_per_month`: Product value normalized over warranty period.
  - `days_past_expiry`: Explicit count of days elapsed past policy expiration.
  - `is_grace_period`: Binary indicator for claims within 15 days past policy expiration.
  - `is_reporting_overdue`: Binary indicator for claims submitted >30 days after fault occurrence.
  - `repair_frequency`: Rate of prior repairs per product operational year.
  - `missing_document_count`: Count of missing mandatory/supporting evidence.

---

## Artifact Paths
```
model/
└── python/
    ├── claim_classifier.joblib
    ├── preprocessor.joblib
    ├── label_encoder.joblib
    ├── feature_columns.json
    └── model_card.md
```
"""
    with open(card_file, "w", encoding="utf-8") as f:
        f.write(content)

    return card_file