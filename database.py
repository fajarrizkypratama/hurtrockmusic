from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

def configure_database(app):
    """Configure database for PostgreSQL"""
    import os
    
    # Use PostgreSQL database from environment variable or create one
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("[WARNING] DATABASE_URL tidak ditemukan, generating default...")
        # Auto-generate DATABASE_URL for local development
        default_db_url = "postgresql://postgres:fajar@localhost:5432/hurtrock"
        os.environ['DATABASE_URL'] = default_db_url
        database_url = default_db_url
        print(f"[INFO] Generated DATABASE_URL: {database_url}")
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        try:
            db.create_all()
            print("[OK] Database PostgreSQL berhasil dikonfigurasi dan tabel dibuat")
            return True
        except Exception as e:
            print(f"[ERROR] Error konfigurasi database: {e}")
            return False