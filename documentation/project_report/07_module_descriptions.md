# Chapter 07: Detailed Module Descriptions

---

## 7.1 Overview of Core Modules

The AssureX backend is structured into specialized services and controllers located within `src/`:

```
src/
├── api/             # HTTP Route Handlers & Controllers
├── core/            # Security, RBAC, Configuration & Logging
├── ml/              # Machine Learning Training, Pipeline & Inference
├── models/          # Relational Database ORM Entities
├── schemas/         # Data Validation & Pydantic DTOs
├── services/        # Business Logic, Rule Engines & Integrations
└── utils/           # Shared Utility Modules (Hashing, Date Math)
```

---

## 7.2 Service Module Deep-Dive

### 1. Ingestion & Preprocessing Service (`src.services.preprocessing_service`)
- Validates inbound claim dictionaries and multipart payloads against Pydantic schemas.
- Parses dates into standard ISO formats and computes chronological intervals (e.g. `product_age_days`, `remaining_warranty_days`, `claim_reporting_days`).
- Normalizes textual fields (trimming, case standardization, enum mapping).

### 2. Deterministic Rule Engine (`src.services.rule_engine`)
- Executes strict Boolean and relational business logic:
  - **Rule 1: Active Warranty & Grace Bounds:** Checks if `remaining_warranty_days >= -15`.
  - **Rule 2: Policy Exclusion Check:** Detects prohibited damage classes (`liquid_spill_damage`, `accidental_damage`, `unauthorized_modification`).
  - **Rule 3: Serial Integrity Verification:** Cross-checks OCR extracted serial numbers against registered database serials.
  - **Rule 4: Temporal Contradiction Check:** Asserts that `claim_submission_date >= purchase_date` and `fault_occurrence_date >= purchase_date`.
  - **Rule 5: Mandatory Document Completeness:** Asserts presence of purchase receipt, warranty card, and product photos.

### 3. Tabular Machine Learning Predictor (`src.ml.predict.ClaimPredictor`)
- Implements a thread-safe singleton predictor.
- Applies the fitted `preprocessor.joblib` pipeline (numeric scaling, one-hot categorical encoding, missing value imputation).
- Invokes `claim_classifier.joblib` (Random Forest Classifier) to produce class probabilities (`[P(Invalid), P(Manual), P(Valid)]`).

### 4. Summary Card Synthesizer & Vision Classifier (`src.services.tm_service`)
- Uses Python Pillow to render a 224x224 RGB Claim Summary Card containing standardized metadata grids, colored status headers, and QR integrity patterns.
- Passes the rendered card to the Teachable Machine (MobileNetV2) vision inference engine.
- Returns class predictions and vision confidence scores.

### 5. Arbitration & Decision Engine (`src.services.decision_service`)
- Computes confidence delta: $|\Delta_{conf}| = |\text{Conf}_{ML} - \text{Conf}_{TM}|$.
- Evaluates consistency status: `STRONG_MATCH` ($\le 0.10$), `ACCEPTABLE` ($\le 0.20$), `WEAK_MATCH` ($\le 0.35$), or `DISAGREEMENT` ($> 0.35$).
- Executes the decision arbitration matrix to yield `AUTO_APPROVE`, `AUTO_REJECT`, or `MANUAL_REVIEW`.

### 6. Audit & Notification Service (`src.services.audit_service` & `notification_service`)
- Writes structured audit records into `audit_logs` table.
- Dispatches webhook notifications and claimant alerts upon claim resolution.