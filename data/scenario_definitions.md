# Claim Scenario Definitions

Total records: **1,500** (500 per class). Seed: **42**.

## Valid Claim (500)

| Scenario | Weight | Meaning |
|----------|-------:|---------|
| complete_active_warranty | 40 | Saari mandatory docs, active warranty, covered fault, serial match |
| extended_warranty_valid | 20 | Extended warranty ke saath clean claim |
| authorized_repair_history | 20 | Authorized repair history, phir bhi valid |
| near_expiry_still_valid | 20 | Expiry ke qareeb (1–20 days left) lekin abhi bhi active |

**Hard rules for Valid:** `warranty_active=yes`, `covered_fault=yes`, `excluded_damage=no`, `proof_of_purchase=yes`, `serial_status=match`, `no contradiction`, `no duplicate`, `mandatory docs complete`, `missing_document_count=0`, `remaining_warranty_days >= 0`.

## Invalid Claim (500)

| Scenario | Weight | Meaning |
|----------|-------:|---------|
| warranty_expired_hard | 30 | Warranty expiry ke 30–400 din baad claim |
| excluded_damage_type | 25 | Drop / liquid / unauthorized modification jaisa excluded damage |
| no_proof_of_purchase | 15 | Receipt + warranty card missing, proof of purchase = **no** |
| duplicate_claim | 15 | Pehle se dia hua duplicate claim |
| serial_mismatch_confirmed | 15 | Serial number documents se confirmed mismatch |

**Hard rules for Invalid:** kam se kam ek hard-fail signal mandatory hai (expired / excluded / no proof / duplicate / serial mismatch).

## Manual Review (500)

| Scenario | Weight | Meaning | proof_of_purchase | Ambiguity Signal |
|----------|-------:|---------|-------------------|------------------|
| missing_mandatory_documents | 22 | Ek mandatory doc missing (receipt) | **uncertain** | missing docs |
| minor_data_contradiction | 18 | Model/serial jaisi choti contradiction (gray area) | yes | contradiction |
| grace_period_boundary | 20 | Expiry ke 1–15 din andar (grace period) — ambiguous | yes | remaining in [-15, 0) |
| unauthorized_repair_uncertain | 16 | Unauthorized repair + missing repair report | yes | repair_authorized=no |
| weak_serial_evidence | 14 | Serial evidence missing / OCR low quality | yes | serial_status=missing_evidence |
| near_reporting_deadline | 10 | 30-din reporting deadline ke bilkul qareeb (24–30) | yes | claim_reporting_days >= 24 |

**Rule:** Manual Review claims clearly invalid nahi honay chahiye — ambiguity / missing evidence / boundary conditions. Har MR row ke paas kam se kam ek ambiguity signal hona chahiye.

## Fields Jo Labels Support Karte Hain

- `warranty_active`, `remaining_warranty_days`
- `covered_fault`, `excluded_damage`
- `proof_of_purchase` (**yes / no / uncertain**), `receipt_available`, `mandatory_docs_complete`
- `serial_status` (match / mismatch / missing_evidence)
- `has_contradiction`, `contradiction_type`
- `is_duplicate`
- `within_reporting_period`, `claim_reporting_days`
- `repair_authorized` (yes / no / none), `repair_history_count`
- `missing_document_count` (excludes n/a repair_report)
- `ocr_quality` (high / medium / low) — Valid claims ~15% medium for realism

## Document States

| Document | Values | Notes |
|----------|--------|-------|
| receipt_available | yes / no | |
| warranty_card_available | yes / no | |
| product_image_available | yes / no | |
| serial_evidence_available | yes / no | |
| fault_evidence_available | yes / no | |
| repair_report_available | yes / no / **n/a** | **n/a when repair_history_count = 0** |

**missing_document_count** counts only `no` values (excludes `n/a`).