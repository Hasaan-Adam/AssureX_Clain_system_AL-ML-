# Chapter 14: Preprocessing & Feature Engineering Pipeline

---

## 14.1 Raw Ingestion & Chronological Feature Extraction

The transformation pipeline converts raw heterogeneous claims into structured numerical vectors through mathematical feature derivation:

```mermaid
flowchart LR
    A["Raw Dates & Text"] --> B["Chronological Delta Engine"]
    B --> C1["product_age_days = claim_date - purchase_date"]
    B --> C2["remaining_warranty_days = expiry_date - claim_date"]
    B --> C3["claim_reporting_days = claim_date - fault_date"]
    
    A --> D["Document Aggregator"]
    D --> E1["missing_document_count = sum(doc_flags == 'no')"]
    D --> E2["mandatory_docs_complete = (receipt == 'yes' & card == 'yes')"]
    
    C1 & C2 & C3 & E1 & E2 --> F["Scikit-Learn ColumnTransformer Pipeline"]
```

---

## 14.2 Preprocessing Subsystem (`src.ml.preprocess_pipeline`)

The production pipeline utilizes `sklearn.compose.ColumnTransformer` with three specialized transformers:

```python
numeric_transformer = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ]
)

categorical_transformer = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ]
)

boolean_transformer = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="constant", fill_value=0)),
    ]
)
```

---

## 14.3 Mathematical Transformations & Imputation

1. **Continuous Feature Standardization:**
   $$z = \frac{x - \mu}{\sigma}$$
   Ensures zero-mean unit-variance for `product_age_days`, `remaining_warranty_days`, `claim_reporting_days`, and `purchase_price`.

2. **Boolean Mapping:**
   String flags (`"yes"`, `"no"`, `"true"`, `"false"`) are mapped deterministically to $\{1, 0\}$.

3. **Label Encoding:**
   Target classes are mapped to discrete integer labels:
   $$\text{Invalid Claim} \mapsto 0, \quad \text{Manual Review} \mapsto 1, \quad \text{Valid Claim} \mapsto 2$$
   Serialized via `label_encoder.joblib` for reproducible decoding.