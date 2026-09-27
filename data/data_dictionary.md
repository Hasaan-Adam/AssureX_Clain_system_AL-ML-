# Warranty Claim Dataset — Data Dictionary

Source: `data/raw/claims_all.csv` → splits in `data/train|validation|test/`.
Rows: 1,500 | Classes: Valid Claim / Invalid Claim / Manual Review (500 each).

## Identifiers

| Column | Type | Description |
|--------|------|-------------|
| claim_id | string | Unique claim ID, format `CLM-00001` |
| label | string | Target class: `Valid Claim`, `Invalid Claim`, `Manual Review` |
| scenario | string | Generator scenario name (see scenario_definitions.md) — **NOT a feature for ML** |
| product_id | string | Registered product ID `PRD-XXX-#####` |
| user_id | string | Claimant user ID `USR-#####` |

## Product

| Column | Type | Description |
|--------|------|-------------|
| product_name | string | e.g. Laptop, Refrigerator, Smartphone |
| product_category | string | `electronics`, `home_appliances`, `mobile_phones` |
| brand | string | Brand name |
| model_number | string | Model code |
| serial_number | string | Product serial |
| serial_status | string | `match`, `mismatch`, `missing_evidence` |

## Purchase & Warranty

| Column | Type | Description |
|--------|------|-------------|
| purchase_date | date (ISO) | Purchase date |
| purchase_price | int | Price in PKR |
| retailer | string | Seller / store name |
| warranty_duration_months | int | Warranty length in months |
| warranty_type | string | `standard` or `extended` |
| warranty_start_date | date | Usually = purchase_date |
| warranty_expiry_date | date | start + duration |
| warranty_active | bool str | `yes` if claim within warranty (grace rules apply for boundary) |
| remaining_warranty_days | int | expiry − claim date (negative = past expiry) |
| proof_of_purchase | string | `yes` (receipt present), `no` (explicitly no proof), `uncertain` (missing docs, MR) |

## Claim & Fault

| Column | Type | Description |
|--------|------|-------------|
| claim_submission_date | date | Date claim filed |
| product_age_days | int | claim date − purchase date |
| fault_occurrence_date | date | When fault happened |
| fault_type | string | Covered OR excluded fault category |
| fault_description | string | Human-readable fault text |
| damage_type | string | Defect / accidental / wear etc. |
| covered_fault | bool str | Whether fault is under coverage (`yes`/`no`) |
| claim_reporting_days | int | Days between fault and claim |
| within_reporting_period | bool str | ≤ 30 days (`yes`/`no`) |
| reporting_deadline_days | int | Policy reporting window (30, constant) |

## Repair History

| Column | Type | Description |
|--------|------|-------------|
| repair_history_count | int | Number of prior repairs |
| last_repair_date | date/empty | Date of last repair |
| repair_authorized | string | `yes`, `no`, `none` |
| previous_replacement | bool str | Product replaced before? |

## Documents (available = yes/no/n/a)

| Column | Type | Description |
|--------|------|-------------|
| receipt_available | bool str | Purchase receipt (`yes`/`no`) |
| warranty_card_available | bool str | Warranty card (`yes`/`no`) |
| product_image_available | bool str | Product photo (`yes`/`no`) |
| serial_evidence_available | bool str | Serial number photo/evidence (`yes`/`no`) |
| fault_evidence_available | bool str | Damage/fault evidence (`yes`/`no`) |
| repair_report_available | string | Repair center report (`yes`/`no`/`n/a` — n/a when no repairs) |
| missing_document_count | int | Count of docs with value `no` (excludes `n/a`, range 0–5) |
| mandatory_docs_complete | bool str | Mandatory set present (`yes`/`no`) |

## Integrity Signals

| Column | Type | Description |
|--------|------|-------------|
| has_contradiction | bool str | Conflicting data detected (`yes`/`no`) |
| contradiction_type | string | none / claim_before_purchase / repair_before_purchase / model_mismatch / serial_conflict / fault_after_claim |
| is_duplicate | bool str | Duplicate claim indicator (`yes`/`no`) |
| excluded_damage | bool str | Damage type excluded by policy (`yes`/`no`) |
| ocr_quality | string | high / medium / low extraction quality |

## Split Policy

| Split | Records | Ratio |
|-------|--------:|------:|
| Train | 1,050 | 70% |
| Validation | 225 | 15% |
| Test | 225 | 15% |

- Stratified by label (350/75/75 per class).
- Same `claim_id` never appears in two splits (CSV or image form).
- Mapping: `data/claim_id_split_map.csv`, `data/claim_id_image_map.csv`.

## ML Feature Notes

Columns **excluded from training** (see `dataset_generator/features.py`):
- Identifiers: `claim_id`, `product_id`, `user_id`
- Target/leakage: `label`, `scenario`
- Raw dates: use derived numerics instead (`product_age_days`, `remaining_warranty_days`, `claim_reporting_days`)
- High cardinality: `serial_number`, `model_number`, `fault_description`, `retailer`, `brand`
- Constant: `reporting_deadline_days`
- Strong label predictor: `proof_of_purchase` (use `receipt_available` + `missing_document_count` instead)