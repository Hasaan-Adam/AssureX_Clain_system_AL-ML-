# AssureX Claim Engine — REST API Documentation 📡

**Base URL:** `http://127.0.0.1:8000/api/v1`  
**Authentication:** HTTP Bearer JWT Token  
**Interactive Docs:** `http://127.0.0.1:8000/docs` (Swagger UI) / `http://127.0.0.1:8000/redoc` (ReDoc)  

---

## 1. Authentication Endpoints

### `POST /auth/login`
Authenticate user credentials and obtain a JWT access token.

- **Request Body:**
```json
{
  "email": "adjuster@assurex.com",
  "password": "SecurePassword123!"
}
```
- **Response (`200 OK`):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "role": "adjuster",
  "user_id": "USR-1002"
}
```

---

## 2. Claim Submission & Evaluation Endpoints

### `POST /claims/evaluate`
Submit a warranty claim payload for instantaneous automated evaluation through the Rule Engine and Dual-AI models.

- **Headers:** `Authorization: Bearer <JWT_TOKEN>`, `Content-Type: application/json`
- **Request Body:**
```json
{
  "claim_id": "CLM-2024-9012",
  "product_id": "PRD-ELE-27927",
  "user_id": "USR-92345",
  "product_name": "Samsung 65\" 4K Neo QLED TV",
  "product_category": "electronics",
  "brand": "Samsung",
  "model_number": "QN65QN90C",
  "serial_number": "ELC-SAM-904751",
  "purchase_date": "2024-03-10",
  "purchase_price": 218000,
  "warranty_duration_months": 24,
  "warranty_type": "standard",
  "claim_submission_date": "2024-08-15",
  "fault_occurrence_date": "2024-08-05",
  "fault_type": "hardware_failure",
  "fault_description": "Vertical colored line distortion on screen panel.",
  "damage_type": "manufacturing_defect",
  "covered_fault": "yes",
  "repair_history_count": 0,
  "receipt_available": "yes",
  "warranty_card_available": "yes",
  "product_image_available": "yes",
  "serial_evidence_available": "yes",
  "fault_evidence_available": "yes"
}
```
- **Response (`200 OK`):**
```json
{
  "claim_id": "CLM-2024-9012",
  "rule_engine_status": "PASS",
  "rule_violations": [],
  "python_model_prediction": "Valid Claim",
  "python_model_confidence": 0.985,
  "tm_model_prediction": "Valid Claim",
  "tm_model_confidence": 0.962,
  "confidence_delta": 0.023,
  "consistency_status": "STRONG_MATCH",
  "final_decision": "AUTO_APPROVE",
  "processed_latency_ms": 38.4,
  "processed_at": "2026-09-24T12:00:00Z"
}
```

---

## 3. Dual-Model Prediction & Comparison

### `GET /predictions/compare/{claim_id}`
Retrieve side-by-side probability breakdown and decision arbitration log for a given claim.

- **Response (`200 OK`):**
```json
{
  "claim_id": "CLM-2024-9012",
  "tabular_ml": {
    "model_version": "v1.0.0",
    "prediction": "Valid Claim",
    "probabilities": {
      "Invalid Claim": 0.005,
      "Manual Review": 0.010,
      "Valid Claim": 0.985
    }
  },
  "vision_tm": {
    "model_version": "v1.0.0-mobilenetv2",
    "prediction": "Valid Claim",
    "probabilities": {
      "Invalid Claim": 0.012,
      "Manual Review": 0.026,
      "Valid Claim": 0.962
    }
  },
  "delta": 0.023,
  "arbitration": {
    "status": "STRONG_MATCH",
    "final_decision": "AUTO_APPROVE",
    "rule_override": false
  }
}
```

---

## 4. Adjuster Review & Adjudication

### `POST /reviews/adjudicate`
Record a human adjuster's manual decision on a flagged claim in the review queue.

- **Request Body:**
```json
{
  "claim_id": "CLM-DEMO-010",
  "adjudication": "APPROVED_GRACE_GOODWILL",
  "notes": "Approved under 15-day grace goodwill policy as fault date occurred 3 days before warranty expiration.",
  "override_reason": "Goodwill customer retention exception"
}
```
- **Response (`200 OK`):**
```json
{
  "review_id": "REV-89210",
  "claim_id": "CLM-DEMO-010",
  "status": "RESOLVED",
  "updated_claim_decision": "APPROVED_BY_ADJUSTER",
  "timestamp": "2026-09-24T12:05:00Z"
}
```