-- 002_claim_and_role_columns.sql
-- Adds the columns required by:
--   * FR xi  : claim_amount, damage/appeal/rejection fields stored on the claim
--   * FR x   : created_by / filing_channel / service_center for claims filed
--               on behalf of a customer by service-centre staff
--   * FR xlvii: distinct processed_at / resolved_at timestamps for the audit trail
--   * role model unification: legacy 'staff' role values migrated to 'service_staff'
--
-- Statements are written to be idempotent-safe on SQLite (ADD COLUMN fails
-- loudly if the column already exists, so run only once on a fresh database or
-- rely on the migration runner in database/migrate.py which checks first).

ALTER TABLE claims ADD COLUMN claim_amount REAL NOT NULL DEFAULT 0.0;
ALTER TABLE claims ADD COLUMN created_by INTEGER;
ALTER TABLE claims ADD COLUMN filing_channel VARCHAR(30) NOT NULL DEFAULT 'self_service';
ALTER TABLE claims ADD COLUMN service_center VARCHAR(120);
ALTER TABLE claims ADD COLUMN rejection_reason TEXT;
ALTER TABLE claims ADD COLUMN escalation_reason TEXT;
ALTER TABLE claims ADD COLUMN appeal_notes TEXT;
ALTER TABLE claims ADD COLUMN processed_at DATETIME;
ALTER TABLE claims ADD COLUMN resolved_at DATETIME;

UPDATE claims SET claim_amount = COALESCE(
    (SELECT purchase_price FROM products WHERE products.id = claims.product_id), 0.0
) WHERE claim_amount = 0.0;

UPDATE users SET role = 'service_staff' WHERE role = 'staff';
