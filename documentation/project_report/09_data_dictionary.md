# Chapter 09: Comprehensive Data Dictionary

---

## 9.1 Overview & Schema Constraints

This data dictionary outlines every column in the AssureX tabular feature dataset (`data/raw/claims_all.csv`) and database tables, specifying types, nullability, allowable values, and business semantics.

---

## 9.2 Claim Dataset Feature Catalog (48 Attributes)

| Attribute Name | Data Type | Nullable | Domain / Enum / Format | Business Meaning |
|---|---|---|---|---|
| `claim_id` | String | No | `CLM-[0-9]{5}` | Primary unique identifier for claim |
| `label` | String | No | `Valid Claim`, `Invalid Claim`, `Manual Review` | Target ground truth classification |
| `scenario` | String | No | 14 predefined scenarios | Synthetic generator scenario descriptor |
| `product_id` | String | No | `PRD-[A-Z]{3}-[0-9]{5}` | Registered product identifier |
| `user_id` | String | No | `USR-[0-9]{5}` | Claimant customer identifier |
| `product_name` | String | No | Free text (e.g. Laptop, Refrigerator) | Consumer product commercial name |
| `product_category`| String | No | `electronics`, `home_appliances`, `mobile_phones` | High-level industry sector |
| `brand` | String | No | Brand names (Samsung, Apple, Dell, etc.) | Original Equipment Manufacturer (OEM) |
| `model_number` | String | No | Model strings (e.g. QN65QN90C) | Manufacturer hardware model code |
| `serial_number` | String | No | Format `[A-Z]{3}-[A-Z]{3}-[0-9]{6}` | Hardware unit serial number |
| `serial_status` | String | No | `match`, `mismatch`, `missing_evidence` | OCR inspection vs DB registration |
| `purchase_date` | Date | No | `YYYY-MM-DD` | Date of official retail purchase |
| `purchase_price` | Integer | No | $> 0$ (in PKR) | Retail purchase price including sales tax |
| `retailer` | String | No | Store / Merchant name | Authorized retailer or e-commerce merchant |
| `warranty_duration_months` | Integer | No | `6, 12, 18, 24, 36, 48` | Standard or extended policy duration |
| `warranty_type` | String | No | `standard`, `extended` | Base OEM coverage vs extended contract |
| `warranty_start_date` | Date | No | `YYYY-MM-DD` | Inception date of warranty |
| `warranty_expiry_date` | Date | No | `YYYY-MM-DD` | Legal expiration date of policy |
| `claim_submission_date` | Date | No | `YYYY-MM-DD` | Timestamp when claim was filed |
| `product_age_days` | Integer | No | Signed integer ($\ge -30$) | Days elapsed between purchase and claim |
| `remaining_warranty_days` | Integer | No | Signed integer | Expiry date minus claim submission date |
| `fault_occurrence_date` | Date | No | `YYYY-MM-DD` | Date user observed defect |
| `fault_type` | String | No | 10 fault categories | Specific technical symptom |
| `fault_description`| String | No | Free text description | User narrative of product failure |
| `damage_type` | String | No | `manufacturing_defect`, `component_failure`, `wear_and_tear`, `accidental_damage`, `unauthorized_modification` | Root cause category of damage |
| `covered_fault` | String | No | `yes`, `no` | Policy coverage indicator |
| `claim_reporting_days` | Integer | No | $\ge 0$ | Days elapsed from fault to claim |
| `within_reporting_period` | String | No | `yes`, `no` | Whether reporting is within 30-day window |
| `reporting_deadline_days`| Integer | No | Fixed at `30` | Contractual reporting deadline |
| `repair_history_count` | Integer | No | $0 \le n \le 5$ | Number of prior warranty repair events |
| `last_repair_date` | Date / Null | Yes | `YYYY-MM-DD` or empty | Date of most recent service center visit |
| `repair_authorized` | String | No | `yes`, `no`, `none` | Authorization status of prior repair |
| `previous_replacement` | String | No | `yes`, `no` | Whether unit was replaced previously |
| `receipt_available` | String | No | `yes`, `no` | Presence of commercial invoice |
| `warranty_card_available` | String | No | `yes`, `no` | Presence of signed warranty card |
| `product_image_available` | String | No | `yes`, `no` | Presence of device overall photo |
| `serial_evidence_available` | String | No | `yes`, `no` | Presence of clear serial sticker photo |
| `fault_evidence_available` | String | No | `yes`, `no` | Presence of diagnostic / damage image |
| `repair_report_available` | String | No | `yes`, `no` | Presence of authorized service center sheet |
| `missing_document_count` | Integer | No | $0 \le n \le 6$ | Total count of missing documents |
| `mandatory_docs_complete` | String | No | `yes`, `no` | Core document bundle completeness |
| `has_contradiction` | String | No | `yes`, `no` | Flag indicating temporal or data conflict |
| `contradiction_type` | String | No | `none`, `claim_before_purchase`, `repair_before_purchase`, `serial_conflict`, `fault_after_claim` | Classification of detected contradiction |
| `is_duplicate` | String | No | `yes`, `no` | Flag indicating duplicate claim submission |
| `proof_of_purchase` | String | No | `yes`, `no` | Consolidated proof of purchase flag |
| `warranty_active` | String | No | `yes`, `no` | Active policy indicator (grace rules apply) |
| `excluded_damage` | String | No | `yes`, `no` | Prohibited damage exclusion flag |
| `ocr_quality` | String | No | `high`, `medium`, `low` | Confidence rating of OCR document scan |