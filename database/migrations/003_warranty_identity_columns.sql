-- 003: Warranty record owns its identity/ownership fields (SRS data dictionary)
-- Aligns the ORM with database/schema.sql:
--   warranties.warranty_number, user_id, serial_number, purchase_date,
--   status, purchase_price, invoice_number, store_name, notes,
--   warranty_duration_months
-- Values are backfilled from the product row each warranty belongs to, so this
-- migration is safe to run against an existing development database.

ALTER TABLE warranties ADD COLUMN warranty_number VARCHAR(100);
ALTER TABLE warranties ADD COLUMN user_id INTEGER REFERENCES users(id);
ALTER TABLE warranties ADD COLUMN serial_number VARCHAR(100);
ALTER TABLE warranties ADD COLUMN purchase_date DATE;
ALTER TABLE warranties ADD COLUMN status VARCHAR(50) DEFAULT 'ACTIVE';
ALTER TABLE warranties ADD COLUMN purchase_price REAL DEFAULT 0.0;
ALTER TABLE warranties ADD COLUMN invoice_number VARCHAR(100);
ALTER TABLE warranties ADD COLUMN store_name VARCHAR(255);
ALTER TABLE warranties ADD COLUMN notes TEXT;
ALTER TABLE warranties ADD COLUMN warranty_duration_months INTEGER;

UPDATE warranties
SET serial_number = (
        SELECT serial_number FROM products WHERE products.id = warranties.product_id
    ),
    purchase_date = COALESCE(
        (SELECT purchase_date FROM products WHERE products.id = warranties.product_id),
        start_date
    ),
    purchase_price = COALESCE(
        (SELECT purchase_price FROM products WHERE products.id = warranties.product_id),
        0.0
    ),
    user_id = (
        SELECT owner_id FROM products WHERE products.id = warranties.product_id
    );

-- Every existing row must end up with a warranty number.
UPDATE warranties
SET warranty_number = 'WRN-LEGACY-' || SUBSTR('00000' || id, -5)
WHERE warranty_number IS NULL OR warranty_number = '';

CREATE UNIQUE INDEX IF NOT EXISTS ix_warranties_warranty_number ON warranties(warranty_number);
CREATE INDEX IF NOT EXISTS ix_warranties_user_id ON warranties(user_id);
CREATE INDEX IF NOT EXISTS ix_warranties_product_id ON warranties(product_id);
CREATE INDEX IF NOT EXISTS ix_warranties_serial_number ON warranties(serial_number);
CREATE INDEX IF NOT EXISTS ix_warranties_status ON warranties(status);
CREATE INDEX IF NOT EXISTS ix_warranties_expiry_date ON warranties(expiry_date);

-- Normalise any legacy 'staff' role rows to the canonical 'service_staff'.
UPDATE users SET role = 'service_staff' WHERE LOWER(role) = 'staff';
