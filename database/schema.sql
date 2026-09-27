-- =============================================================================
-- AssureX Claim Engine - Database Schema DDL
-- Compatible with SQLite 3.x and PostgreSQL 12+
-- =============================================================================

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'customer',
    is_active BOOLEAN NOT NULL DEFAULT 1,
    phone VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_users_email ON users(email);
CREATE INDEX IF NOT EXISTS ix_users_role ON users(role);

-- 2. Products Table
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    brand VARCHAR(100) NOT NULL,
    serial_prefix VARCHAR(50),
    msrp REAL NOT NULL DEFAULT 0.0,
    warranty_months INTEGER NOT NULL DEFAULT 12,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_products_model_name ON products(model_name);
CREATE INDEX IF NOT EXISTS ix_products_category ON products(category);
CREATE INDEX IF NOT EXISTS ix_products_brand ON products(brand);
CREATE INDEX IF NOT EXISTS ix_products_serial_prefix ON products(serial_prefix);

-- 3. Warranties Table
CREATE TABLE IF NOT EXISTS warranties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    warranty_number VARCHAR(100) NOT NULL UNIQUE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
    serial_number VARCHAR(100) NOT NULL,
    purchase_date DATE NOT NULL,
    expiry_date DATE NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE',
    purchase_price REAL NOT NULL DEFAULT 0.0,
    invoice_number VARCHAR(100),
    store_name VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_warranties_warranty_number ON warranties(warranty_number);
CREATE INDEX IF NOT EXISTS ix_warranties_user_id ON warranties(user_id);
CREATE INDEX IF NOT EXISTS ix_warranties_product_id ON warranties(product_id);
CREATE INDEX IF NOT EXISTS ix_warranties_serial_number ON warranties(serial_number);
CREATE INDEX IF NOT EXISTS ix_warranties_status ON warranties(status);
CREATE INDEX IF NOT EXISTS ix_warranties_purchase_date ON warranties(purchase_date);
CREATE INDEX IF NOT EXISTS ix_warranties_expiry_date ON warranties(expiry_date);

-- 4. Claims Table
CREATE TABLE IF NOT EXISTS claims (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    claim_number VARCHAR(100) NOT NULL UNIQUE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    warranty_id INTEGER NOT NULL REFERENCES warranties(id) ON DELETE CASCADE,
    fault_type VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    claim_amount REAL NOT NULL DEFAULT 0.0,
    status VARCHAR(50) NOT NULL DEFAULT 'submitted',
    ai_decision VARCHAR(50),
    final_decision VARCHAR(50),
    fraud_score REAL DEFAULT 0.0,
    ai_confidence REAL DEFAULT 0.0,
    model_agreement_score REAL DEFAULT 1.0,
    rejection_reason TEXT,
    escalation_reason TEXT,
    appeal_notes TEXT,
    submitted_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP WITH TIME ZONE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_claims_claim_number ON claims(claim_number);
CREATE INDEX IF NOT EXISTS ix_claims_user_id ON claims(user_id);
CREATE INDEX IF NOT EXISTS ix_claims_warranty_id ON claims(warranty_id);
CREATE INDEX IF NOT EXISTS ix_claims_status ON claims(status);
CREATE INDEX IF NOT EXISTS ix_claims_fault_type ON claims(fault_type);

-- 5. Documents Table
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    claim_id INTEGER REFERENCES claims(id) ON DELETE CASCADE,
    warranty_id INTEGER REFERENCES warranties(id) ON DELETE CASCADE,
    document_type VARCHAR(100) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    file_hash VARCHAR(64) NOT NULL,
    ocr_extracted_text TEXT,
    ocr_confidence REAL,
    ocr_metadata JSON,
    uploaded_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_documents_claim_id ON documents(claim_id);
CREATE INDEX IF NOT EXISTS ix_documents_warranty_id ON documents(warranty_id);
CREATE INDEX IF NOT EXISTS ix_documents_document_type ON documents(document_type);
CREATE INDEX IF NOT EXISTS ix_documents_file_hash ON documents(file_hash);

-- 6. Repairs Table
CREATE TABLE IF NOT EXISTS repairs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    claim_id INTEGER NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
    repair_partner VARCHAR(255),
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    estimated_cost REAL NOT NULL DEFAULT 0.0,
    actual_cost REAL,
    tracking_number VARCHAR(100),
    notes TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_repairs_claim_id ON repairs(claim_id);
CREATE INDEX IF NOT EXISTS ix_repairs_status ON repairs(status);

-- 7. Predictions Table
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    claim_id INTEGER NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
    model_name VARCHAR(100) NOT NULL,
    prediction_result VARCHAR(50) NOT NULL,
    confidence_score REAL NOT NULL DEFAULT 0.0,
    fraud_risk_score REAL NOT NULL DEFAULT 0.0,
    feature_importance JSON,
    raw_output JSON,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_predictions_claim_id ON predictions(claim_id);
CREATE INDEX IF NOT EXISTS ix_predictions_model_name ON predictions(model_name);

-- 8. Reviews Table
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    claim_id INTEGER NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
    reviewer_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    previous_status VARCHAR(50) NOT NULL,
    new_status VARCHAR(50) NOT NULL,
    decision VARCHAR(50) NOT NULL,
    reasoning TEXT NOT NULL,
    notes TEXT,
    reviewed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_reviews_claim_id ON reviews(claim_id);
CREATE INDEX IF NOT EXISTS ix_reviews_reviewer_id ON reviews(reviewer_id);

-- 9. Notifications Table
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50) NOT NULL DEFAULT 'system_alert',
    channel VARCHAR(50) NOT NULL DEFAULT 'in_app',
    severity VARCHAR(20) NOT NULL DEFAULT 'INFO',
    is_read BOOLEAN NOT NULL DEFAULT 0,
    metadata_json JSON,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS ix_notifications_is_read ON notifications(is_read);
CREATE INDEX IF NOT EXISTS ix_notifications_type ON notifications(notification_type);

-- 10. Audit Logs Table
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id VARCHAR(100),
    old_values JSON,
    new_values JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS ix_audit_logs_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS ix_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS ix_audit_logs_created_at ON audit_logs(created_at);

-- 11. Settings Table
CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key VARCHAR(100) NOT NULL UNIQUE,
    value JSON NOT NULL,
    description TEXT,
    updated_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_settings_key ON settings(key);