# Chapter 04: Scope, Assumptions, and Operational Constraints

---

## 4.1 In-Scope Capabilities

The AssureX Claim Engine implements the following operational scope:
- **Product Categories Supported:** Consumer Electronics (Laptops, TVs, Audio, Desktops), Home Appliances (Refrigerators, Washing Machines, Air Conditioners, Microwaves), and Mobile Devices (Smartphones, Tablets, Smartwatches).
- **Claim Decision Outcomes:** Automated classification into `Valid Claim`, `Invalid Claim`, and `Manual Review`.
- **Policy Verification Rules:** Verification of active warranty windows, 15-day post-expiration grace periods, 30-day fault reporting limits, serial number validation, document completeness checks, duplicate submission detection, and unauthorized repair exclusions.
- **Dual-Model Inference & Arbitration:** Simultaneous inference over Tabular Machine Learning and Computer Vision summary card models with automated discrepancy routing.
- **Web Console & REST API:** Full administrative adjuster portal, claim history explorer, real-time analytics dashboard, and OpenAPI-compliant RESTful endpoints.

---

## 4.2 Out-of-Scope Boundaries

To maintain high focus and architectural integrity, the following capabilities are explicitly designated as out-of-scope for the current version:
- Direct physical repair depot robotics or automated hardware parts dispatching.
- Real-time banking wire transfer processing (the engine authorizes payment status, leaving disbursement execution to external ERP/treasury integrations).
- End-user legal dispute arbitration beyond the structured claims review portal.

---

## 4.3 Key Assumptions

1. **Synthetic Data Realism:** The 1,500-sample benchmark dataset accurately reflects real-world empirical claim distributions, failure modes, and fraud vectors.
2. **Standardized Image Quality:** Claim receipts and summary card images uploaded to the system meet minimum OCR legibility standards (resolution $\ge 300\times300$ pixels).
3. **Temporal Monotonicity:** Purchase dates, warranty start dates, defect occurrence dates, and claim filing timestamps follow standard ISO 8601 calendar chronologies.

---

## 4.4 Technical and Operational Constraints

| Constraint Type | Specification / Limit | Rationale |
|---|---|---|
| **Programming Language** | Python 3.11 / 3.12 | Standard enterprise ecosystem for AI, FastAPI, and data engineering |
| **API Latency** | $\le 100\text{ ms}$ (Target: $\le 50\text{ ms}$) | High-throughput e-commerce checkout and claims integration |
| **Model Size** | $\le 100\text{ MB}$ total artifacts | Lightweight edge and containerized microservice deployment |
| **Database** | SQLite 3 (SQLAlchemy ORM) | Zero-configuration portability with standard SQL compliance |
| **Storage Formats** | JPEG / PNG for images; JSON / CSV for metadata | Maximum cross-platform interoperability |