
```python
#!/usr/bin/env python3
"""
Script untuk update database schema dengan fitur-fitur baru
Jalankan dengan: python update_database_schema.py
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, ProgrammingError

# Database URL dari environment variable
DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    print("[ERROR] DATABASE_URL tidak ditemukan di environment variables")
    exit(1)

# Create engine
engine = create_engine(DATABASE_URL)

def execute_sql(sql, description):
    """Execute SQL dan handle errors"""
    try:
        with engine.connect() as conn:
            conn.execute(text(sql))
            conn.commit()
            print(f"[OK] {description}")
            return True
    except (OperationalError, ProgrammingError) as e:
        if "already exists" in str(e) or "duplicate column" in str(e):
            print(f"[SKIP] {description} - sudah ada")
            return True
        else:
            print(f"[ERROR] {description} - {str(e)}")
            return False

def main():
    print("=" * 60)
    print("MEMULAI UPDATE DATABASE SCHEMA")
    print("=" * 60)
    
    # 1. Update tabel products - tambah kolom GTIN jika belum ada
    execute_sql(
        "ALTER TABLE products ADD COLUMN IF NOT EXISTS gtin VARCHAR(100) UNIQUE;",
        "Tambah kolom GTIN ke tabel products"
    )
    
    # 2. Update tabel products - tambah kolom slug jika belum ada
    execute_sql(
        "ALTER TABLE products ADD COLUMN IF NOT EXISTS slug VARCHAR(255) UNIQUE;",
        "Tambah kolom slug ke tabel products"
    )
    
    # 3. Update tabel orders - tambah kolom untuk kasir/POS
    execute_sql(
        "ALTER TABLE orders ADD COLUMN IF NOT EXISTS source_type VARCHAR(20) DEFAULT 'online';",
        "Tambah kolom source_type ke tabel orders"
    )
    
    execute_sql(
        "ALTER TABLE orders ADD COLUMN IF NOT EXISTS buyer_name VARCHAR(200);",
        "Tambah kolom buyer_name ke tabel orders"
    )
    
    execute_sql(
        "ALTER TABLE orders ADD COLUMN IF NOT EXISTS pos_user_id INTEGER REFERENCES users(id);",
        "Tambah kolom pos_user_id ke tabel orders"
    )
    
    execute_sql(
        "ALTER TABLE orders ADD COLUMN IF NOT EXISTS paid_at TIMESTAMP;",
        "Tambah kolom paid_at ke tabel orders"
    )
    
    execute_sql(
        "ALTER TABLE orders ADD COLUMN IF NOT EXISTS local_transaction_id VARCHAR(100);",
        "Tambah kolom local_transaction_id ke tabel orders"
    )
    
    # 4. Update tabel products - tambah kolom stock management
    execute_sql(
        "ALTER TABLE products ADD COLUMN IF NOT EXISTS minimum_stock INTEGER DEFAULT 5;",
        "Tambah kolom minimum_stock ke tabel products"
    )
    
    execute_sql(
        "ALTER TABLE products ADD COLUMN IF NOT EXISTS low_stock_threshold INTEGER DEFAULT 10;",
        "Tambah kolom low_stock_threshold ke tabel products"
    )
    
    # 5. Buat tabel product_images jika belum ada
    execute_sql(
        """
        CREATE TABLE IF NOT EXISTS product_images (
            id SERIAL PRIMARY KEY,
            product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
            image_url VARCHAR(255) NOT NULL,
            is_thumbnail BOOLEAN DEFAULT FALSE,
            display_order INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        "Buat tabel product_images"
    )
    
    # 6. Buat tabel invoices jika belum ada
    execute_sql(
        """
        CREATE TABLE IF NOT EXISTS invoices (
            id SERIAL PRIMARY KEY,
            invoice_number VARCHAR(50) UNIQUE NOT NULL,
            order_id INTEGER REFERENCES orders(id),
            customer_name VARCHAR(200) NOT NULL,
            customer_email VARCHAR(120),
            customer_phone VARCHAR(20),
            customer_address TEXT,
            subtotal NUMERIC(10,2) NOT NULL,
            tax_amount NUMERIC(10,2) DEFAULT 0,
            discount_amount NUMERIC(10,2) DEFAULT 0,
            shipping_cost NUMERIC(10,2) DEFAULT 0,
            total_amount NUMERIC(10,2) NOT NULL,
            status VARCHAR(20) DEFAULT 'Pending',
            payment_method VARCHAR(50),
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            issued_by INTEGER REFERENCES users(id)
        );
        """,
        "Buat tabel invoices"
    )
    
    # 7. Buat tabel invoice_items jika belum ada
    execute_sql(
        """
        CREATE TABLE IF NOT EXISTS invoice_items (
            id SERIAL PRIMARY KEY,
            invoice_id INTEGER NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
            item_name VARCHAR(200) NOT NULL,
            description TEXT,
            quantity INTEGER NOT NULL,
            unit_price NUMERIC(10,2) NOT NULL
        );
        """,
        "Buat tabel invoice_items"
    )
    
    # 8. Buat tabel cashier_sessions jika belum ada
    execute_sql(
        """
        CREATE TABLE IF NOT EXISTS cashier_sessions (
            id SERIAL PRIMARY KEY,
            cashier_user_id INTEGER NOT NULL REFERENCES users(id),
            session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            session_end TIMESTAMP,
            opening_cash NUMERIC(10,2) DEFAULT 0,
            closing_cash NUMERIC(10,2),
            expected_cash NUMERIC(10,2),
            cash_difference NUMERIC(10,2),
            total_transactions INTEGER DEFAULT 0,
            total_sales NUMERIC(10,2) DEFAULT 0,
            cash_sales NUMERIC(10,2) DEFAULT 0,
            card_sales NUMERIC(10,2) DEFAULT 0,
            status VARCHAR(20) DEFAULT 'active',
            notes TEXT
        );
        """,
        "Buat tabel cashier_sessions"
    )
    
    # 9. Buat tabel offline_transactions jika belum ada
    execute_sql(
        """
        CREATE TABLE IF NOT EXISTS offline_transactions (
            id SERIAL PRIMARY KEY,
            local_transaction_id VARCHAR(100) UNIQUE NOT NULL,
            cashier_user_id INTEGER NOT NULL REFERENCES users(id),
            subtotal NUMERIC(10,2) NOT NULL,
            tax_amount NUMERIC(10,2) DEFAULT 0,
            discount_amount NUMERIC(10,2) DEFAULT 0,
            total_amount NUMERIC(10,2) NOT NULL,
            payment_method VARCHAR(50) NOT NULL,
            payment_amount NUMERIC(10,2) NOT NULL,
            change_amount NUMERIC(10,2) DEFAULT 0,
            customer_name VARCHAR(200),
            customer_phone VARCHAR(20),
            customer_email VARCHAR(120),
            sync_status VARCHAR(20) DEFAULT 'pending',
            sync_attempts INTEGER DEFAULT 0,
            last_sync_attempt TIMESTAMP,
            sync_error_message TEXT,
            transaction_date TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            synced_at TIMESTAMP,
            offline_data TEXT
        );
        """,
        "Buat tabel offline_transactions"
    )
    
    # 10. Buat tabel offline_transaction_items jika belum ada
    execute_sql(
        """
        CREATE TABLE IF NOT EXISTS offline_transaction_items (
            id SERIAL PRIMARY KEY,
            offline_transaction_id INTEGER NOT NULL REFERENCES offline_transactions(id) ON DELETE CASCADE,
            product_id INTEGER NOT NULL REFERENCES products(id),
            product_name VARCHAR(200) NOT NULL,
            product_price NUMERIC(10,2) NOT NULL,
            quantity INTEGER NOT NULL,
            subtotal NUMERIC(10,2) NOT NULL,
            discount_percent NUMERIC(5,2) DEFAULT 0,
            discount_amount NUMERIC(10,2) DEFAULT 0,
            stock_reduced BOOLEAN DEFAULT FALSE
        );
        """,
        "Buat tabel offline_transaction_items"
    )
    
    # 11. Update tabel chat_messages - tambah kolom media
    execute_sql(
        "ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS media_url VARCHAR(500);",
        "Tambah kolom media_url ke tabel chat_messages"
    )
    
    execute_sql(
        "ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS media_type VARCHAR(20);",
        "Tambah kolom media_type ke tabel chat_messages"
    )
    
    execute_sql(
        "ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS media_filename VARCHAR(255);",
        "Tambah kolom media_filename ke tabel chat_messages"
    )
    
    # 12. Buat index untuk performa
    execute_sql(
        "CREATE INDEX IF NOT EXISTS idx_products_gtin ON products(gtin);",
        "Buat index untuk products.gtin"
    )
    
    execute_sql(
        "CREATE INDEX IF NOT EXISTS idx_products_slug ON products(slug);",
        "Buat index untuk products.slug"
    )
    
    execute_sql(
        "CREATE INDEX IF NOT EXISTS idx_orders_local_transaction_id ON orders(local_transaction_id);",
        "Buat index untuk orders.local_transaction_id"
    )
    
    execute_sql(
        "CREATE INDEX IF NOT EXISTS idx_product_images_product_id ON product_images(product_id);",
        "Buat index untuk product_images.product_id"
    )
    
    execute_sql(
        "CREATE INDEX IF NOT EXISTS idx_offline_transactions_sync_status ON offline_transactions(sync_status);",
        "Buat index untuk offline_transactions.sync_status"
    )
    
    print("\n" + "=" * 60)
    print("UPDATE DATABASE SCHEMA SELESAI")
    print("=" * 60)

if __name__ == "__main__":
    main()
```
