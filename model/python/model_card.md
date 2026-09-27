# Model Card: AssureX Claim Classifier (v1.0.0-test)

## Model Overview
- **Model Name:** AssureX Claim Classifier
- **Model Version:** `v1.0.0-test`
- **Algorithm:** `XGBoost`
- **Framework:** `xgboost`
- **Registration Date:** `2026-09-27T17:45:43.766064+00:00`
- **Status:** `active`
- **SRS Requirement (>=85% Accuracy):** `PASSED`

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
| Validation | Accuracy | 98.57% | >= 85.00% |
| Validation | Macro F1 | 0.9857 | - |
| Test | Accuracy | 90.11% | >= 85.00% |
| Test | Macro F1 | 0.9011 | - |
| Test | Weighted F1 | 0.9011 | - |

---

## Hyperparameters
```json
{
  "objective": "multi:softprob",
  "base_score": null,
  "booster": null,
  "callbacks": null,
  "colsample_bylevel": null,
  "colsample_bynode": null,
  "colsample_bytree": 0.9,
  "device": null,
  "early_stopping_rounds": null,
  "enable_categorical": true,
  "eval_metric": "mlogloss",
  "feature_types": null,
  "feature_weights": null,
  "gamma": null,
  "grow_policy": null,
  "importance_type": null,
  "interaction_constraints": null,
  "learning_rate": 0.08,
  "max_bin": null,
  "max_cat_threshold": null,
  "max_cat_to_onehot": null,
  "max_delta_step": null,
  "max_depth": 6,
  "max_leaves": null,
  "min_child_weight": null,
  "missing": NaN,
  "monotone_constraints": null,
  "multi_strategy": null,
  "n_estimators": 150,
  "n_jobs": null,
  "num_parallel_tree": null,
  "random_state": 42,
  "reg_alpha": null,
  "reg_lambda": null,
  "sampling_method": null,
  "scale_pos_weight": null,
  "subsample": 0.9,
  "tree_method": null,
  "validate_parameters": null,
  "verbosity": null
}
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
