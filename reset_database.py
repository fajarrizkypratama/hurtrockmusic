
#!/usr/bin/env python3
"""
Script to reset and reinitialize the database properly
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import from main.py to ensure proper initialization
from main import app, db
import models
from werkzeug.security import generate_password_hash

def reset_database():
    """Reset and reinitialize the database"""
    print("[INFO] Starting database reset...")
    
    with app.app_context():
        try:
            # Rollback any pending transactions first
            db.session.rollback()
            
            # Drop all tables
            print("[INFO] Dropping all tables...")
            db.drop_all()
            
            # Create all tables fresh with current schema
            print("[INFO] Creating fresh tables...")
            db.create_all()
            
            # Create default admin user
            print("[INFO] Creating default admin user...")
            admin_user = models.User(
                email="admin@hurtrock.com",
                password_hash=generate_password_hash("admin123"),
                name="Administrator",
                role="admin"
            )
            db.session.add(admin_user)
            
            # Create default store profile
            print("[INFO] Creating default store profile...")
            store_profile = models.StoreProfile(
                store_name='Hurtrock Music Store',
                store_tagline='Toko Alat Musik Terpercaya',
                store_address='Jl. Musik Raya No. 123, RT/RW 001/002, Kelurahan Musik, Kecamatan Harmoni',
                store_city='Jakarta Selatan',
                store_postal_code='12345',
                store_phone='0821-1555-8035',
                store_email='info@hurtrock.com',
                store_website='https://hurtrock.com',
                whatsapp_number='6282115558035',
                operating_hours='Senin - Sabtu: 09:00 - 21:00\nMinggu: 10:00 - 18:00',
                branch_name='Cabang Pusat',
                branch_code='HRT-001'
            )
            db.session.add(store_profile)
            
            # Create sample categories
            categories = [
                {'name': 'Gitar', 'description': 'Gitar akustik dan elektrik'},
                {'name': 'Bass', 'description': 'Bass elektrik dan akustik'},
                {'name': 'Drum', 'description': 'Drum kit dan perkusi'},
                {'name': 'Keyboard', 'description': 'Keyboard dan piano digital'},
                {'name': 'Sound System', 'description': 'Speaker, mixer, dan audio equipment'},
            ]
            
            print("[INFO] Creating sample categories...")
            for cat_data in categories:
                category = models.Category(**cat_data)
                db.session.add(category)
            
            # Create sample suppliers
            suppliers = [
                {
                    'name': 'Swelee Music Store',
                    'contact_person': 'Swelee',
                    'email': 'contact@swelee.com',
                    'phone': '021-1234-5678',
                    'company': 'PT Swelee Musik Indonesia'
                },
                {
                    'name': 'Media Recording Tech',
                    'contact_person': 'Media Recording',
                    'email': 'info@mediarecording.com',
                    'phone': '021-8765-4321',
                    'company': 'CV Media Recording Technology'
                }
            ]
            
            print("[INFO] Creating sample suppliers...")
            for sup_data in suppliers:
                supplier = models.Supplier(**sup_data)
                db.session.add(supplier)
            
            # Create sample shipping services
            shipping_services = [
                {
                    'name': 'JNE Regular',
                    'code': 'jne_reg',
                    'base_price': 15000,
                    'price_per_kg': 5000,
                    'min_days': 2,
                    'max_days': 4
                },
                {
                    'name': 'JNE Express',
                    'code': 'jne_exp',
                    'base_price': 25000,
                    'price_per_kg': 8000,
                    'min_days': 1,
                    'max_days': 2
                }
            ]
            
            print("[INFO] Creating sample shipping services...")
            for ship_data in shipping_services:
                service = models.ShippingService(**ship_data)
                db.session.add(service)
            
            # Commit all changes
            db.session.commit()
            
            print("[SUCCESS] Database reset completed successfully!")
            print(f"[INFO] Default admin login:")
            print(f"        Email: admin@hurtrock.com")
            print(f"        Password: admin123")
            
        except Exception as e:
            print(f"[ERROR] Database reset failed: {e}")
            db.session.rollback()
            return False
        
        return True

if __name__ == "__main__":
    if reset_database():
        sys.exit(0)
    else:
        sys.exit(1)
