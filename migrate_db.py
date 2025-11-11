#!/usr/bin/env python3
"""
Auto database migration script
Ensures all tables and columns in models.py exist in PostgreSQL
Skips if already present
"""
import os
from flask import Flask
from database import db
import models  # pastikan ini mengimpor semua model kamu
from sqlalchemy import inspect, text

# --- Flask app setup ---
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL",
    "postgresql://fajar:fajar@localhost/hurtrock"  # fallback default
)

app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

db.init_app(app)

# --- Auto Migration Logic ---
def column_exists(table_name, column_name):
    """Check apakah kolom sudah ada"""
    try:
        query = text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = :table_name AND column_name = :column_name
        """)
        result = db.session.execute(query, {"table_name": table_name, "column_name": column_name})
        return result.fetchone() is not None
    except Exception as e:
        print(f"⚠️  Error checking {table_name}.{column_name}: {e}")
        return False


def auto_add_missing_columns():
    """Tambahkan kolom dari models.py yang belum ada di database"""
    try:
        inspector = inspect(db.engine)
        connection = db.engine.connect()

        # Iterasi semua model yang terdaftar di registry baru
        for mapper in db.Model.registry.mappers:
            model = mapper.class_
            table_name = model.__tablename__
            print(f"\n🔍 Checking table: {table_name}")

            # Pastikan tabel ada
            db.create_all()

            for column in model.__table__.columns:
                if not column_exists(table_name, column.name):
                    col_type = str(column.type)
                    nullable = "NULL" if column.nullable else "NOT NULL"
                    default = ""

                    if column.default is not None and hasattr(column.default, "arg"):
                        default_val = column.default.arg
                        if isinstance(default_val, str):
                            default = f"DEFAULT '{default_val}'"
                        else:
                            default = f"DEFAULT {default_val}"

                    sql = f"ALTER TABLE {table_name} ADD COLUMN {column.name} {col_type} {nullable} {default};"
                    try:
                        connection.execute(text(sql))
                        print(f"✅ Added column: {column.name} ({col_type})")
                    except Exception as e:
                        print(f"⚠️  Gagal menambah kolom {column.name}: {e}")
                else:
                    print(f"⏩ Column already exists: {column.name}")

        connection.close()
        print("\n✅ Auto migration complete!")
        db.session.commit()
        return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        db.session.rollback()
        return False


def migrate_database():
    """Jalankan auto migration"""
    with app.app_context():
        print("🛠️  Running auto migration...")
        db.create_all()  # pastikan semua tabel ada
        auto_add_missing_columns()


if __name__ == "__main__":
    migrate_database()

