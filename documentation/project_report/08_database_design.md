# Chapter 08: Database Design & Entity-Relationship Modeling

---

## 8.1 Entity-Relationship (ER) Architecture

The AssureX Claim Engine employs a 3NF normalized relational schema designed for SQLite / PostgreSQL via SQLAlchemy ORM.

```mermaid
erDiagram
    USERS ||--o{ CLAIMS : "submits"
    USERS ||--o{ AUDIT_LOGS : "triggers"
    PRODUCTS ||--o{ WARRANTIES : "registers"
    PRODUCTS ||--o{ CLAIMS : "subject of"
    WARRANTIES ||--o{ CLAIMS : "authorizes"
    CLAIMS ||--o{ DOCUMENTS : "attaches"
    CLAIMS ||--o{ PREDICTIONS : "evaluates"
    CLAIMS ||--o{ REVIEWS : "undergoes"
    CLAIMS ||--o{ NOTIFICATIONS : "generates"

    USERS {
        string user_id PK
        string email UK
        string full_name
        string role
        string password_hash
        datetime created_at
    }

    PRODUCTS {
        string product_id PK
        string product_name
        string category
        string brand
        string model_number
        string serial_number UK
    }

    WARRANTIES {
        string warranty_id PK
        string product_id FK
        date start_date
        date expiry_date
        integer duration_months
        string warranty_type
        string status
    }

    CLAIMS {
        string claim_id PK
        string user_id FK
        string product_id FK
        string warranty_id FK
        date claim_date
        date fault_date
        string fault_type
        string damage_type
        string rule_status
        string final_decision
        string current_status
    }

    DOCUMENTS {
        string doc_id PK
        string claim_id FK
        string document_type
        string file_path
        string sha256_hash UK
        datetime uploaded_at
    }

    PREDICTIONS {
        string prediction_id PK
        string claim_id FK
        string python_prediction
        float python_confidence
        string tm_prediction
        float tm_confidence
        float confidence_delta
        string consistency_status
    }

    REVIEWS {
        string review_id PK
        string claim_id FK
        string reviewer_id FK
        string decision
        text notes
        datetime reviewed_at
    }
```

---

## 8.2 Indexing & Performance Optimization

To guarantee sub-5ms database lookups during high-concurrency API evaluation:
1. **Document Deduplication Index:** Unique B-tree index on `documents.sha256_hash` to detect duplicate file uploads in $O(1)$ time.
2. **Serial Number Lookups:** Unique index on `products.serial_number` to cross-reference OCR extractions instantly.
3. **Claim Filter Indexes:** Composite index on `claims(current_status, final_decision, claim_date)` for rapid adjuster dashboard filtering and pagination.