"""
Sample data for Hurtrock Music Store
Run this script to populate the database with sample products and categories
"""

from main import app
from database import db
from models import Category, Product, ShippingService, Supplier, User, StoreProfile
from werkzeug.security import generate_password_hash
from datetime import datetime

def create_sample_data():
    with app.app_context():
        # Check if data already exists
        if Category.query.first() and Product.query.count() > 5:
            print("Sample data already exists!")
            return

        # Create admin user if not exists
        admin_email = "admin@hurtrock.com"
        admin_user = User.query.filter_by(email=admin_email).first()
        if not admin_user:
            admin_user = User(
                email=admin_email,
                password_hash=generate_password_hash("admin123"),
                name="Administrator",
                role="admin"
            )
            db.session.add(admin_user)
            db.session.commit()
            print(f"[OK] Admin user created: {admin_email}")

        # Create store profile if not exists
        store_profile = StoreProfile.get_active_profile()
        if not store_profile:
            store_profile = StoreProfile(
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
            db.session.commit()
            print("[OK] Store profile created")

        # Create categories
        categories_data = [
            {
                'name': 'Gitar',
                'description': 'Koleksi gitar akustik dan elektrik berkualitas tinggi dari berbagai brand terkenal',
                'image_url': 'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=400'
            },
            {
                'name': 'Bass',
                'description': 'Bass elektrik dan akustik dengan kualitas suara yang luar biasa',
                'image_url': 'https://images.unsplash.com/photo-1520637736862-4d197d17c2a2?w=400'
            },
            {
                'name': 'Drum',
                'description': 'Set drum lengkap dan aksesoris perkusi untuk segala genre musik',
                'image_url': 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400'
            },
            {
                'name': 'Keyboard',
                'description': 'Piano digital dan keyboard sintetizer dengan teknologi terdepan',
                'image_url': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400'
            },
            {
                'name': 'Sound System',
                'description': 'Speaker, mixer, amplifier dan peralatan audio profesional',
                'image_url': 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400'
            },
            {
                'name': 'Aksesoris',
                'description': 'Berbagai aksesoris musik dan peralatan pendukung untuk musisi',
                'image_url': 'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=400'
            }
        ]

        category_objects = []
        for cat_data in categories_data:
            existing = Category.query.filter_by(name=cat_data['name']).first()
            if not existing:
                category = Category(
                    name=cat_data['name'],
                    description=cat_data['description'],
                    image_url=cat_data['image_url'],
                    is_active=True
                )
                db.session.add(category)
                category_objects.append(category)
            else:
                category_objects.append(existing)

        db.session.flush()  # Get category IDs

        # Create suppliers
        suppliers_data = [
            {
                'name': 'PT. Music Indonesia',
                'contact_person': 'Budi Santoso',
                'email': 'budi@musicindonesia.com',
                'phone': '021-12345678',
                'address': 'Jl. Musik Raya No. 123, Jakarta Selatan',
                'company': 'PT. Music Indonesia',
                'notes': 'Supplier utama untuk produk Yamaha dan Roland'
            },
            {
                'name': 'CV. Harmoni Nada',
                'contact_person': 'Siti Rahayu',
                'email': 'siti@harmoninada.co.id',
                'phone': '021-87654321',
                'address': 'Jl. Harmoni No. 456, Jakarta Pusat',
                'company': 'CV. Harmoni Nada',
                'notes': 'Spesialis gitar Fender dan Gibson'
            },
            {
                'name': 'UD. Drum Center',
                'contact_person': 'Ahmad Fadli',
                'email': 'ahmad@drumcenter.com',
                'phone': '021-11223344',
                'address': 'Jl. Beat No. 789, Bandung',
                'company': 'UD. Drum Center',
                'notes': 'Distributor drum Pearl dan Tama'
            },
            {
                'name': 'Swelee Music Store',
                'contact_person': 'John Swelee',
                'email': 'contact@swelee.com',
                'phone': '021-555-0101',
                'address': 'Jl. Musik Digital No. 45, Jakarta Barat',
                'company': 'PT. Swelee Indonesia',
                'notes': 'Supplier peralatan musik digital dan aksesoris premium'
            },
            {
                'name': 'Media Recording Tech',
                'contact_person': 'Sarah Mitchell',
                'email': 'sales@mediarecordingtech.com',
                'phone': '021-555-0202',
                'address': 'Jl. Studio Raya No. 78, Jakarta Selatan',
                'company': 'CV. Media Recording Technology',
                'notes': 'Spesialis peralatan recording dan produksi musik profesional'
            }
        ]

        supplier_objects = []
        for supplier_data in suppliers_data:
            existing = Supplier.query.filter_by(name=supplier_data['name']).first()
            if not existing:
                supplier = Supplier(
                    name=supplier_data['name'],
                    contact_person=supplier_data['contact_person'],
                    email=supplier_data['email'],
                    phone=supplier_data['phone'],
                    address=supplier_data['address'],
                    company=supplier_data['company'],
                    notes=supplier_data['notes'],
                    is_active=True
                )
                db.session.add(supplier)
                supplier_objects.append(supplier)
            else:
                supplier_objects.append(existing)

        db.session.flush()  # Get supplier IDs

        # Create shipping services
        shipping_data = [
            {
                'name': 'JNE Regular',
                'code': 'jne_reg',
                'base_price': 15000,
                'price_per_kg': 8000,
                'price_per_km': 0.5,
                'volume_factor': 6000,
                'min_days': 2,
                'max_days': 4
            },
            {
                'name': 'JNE Express',
                'code': 'jne_exp',
                'base_price': 25000,
                'price_per_kg': 12000,
                'price_per_km': 0.8,
                'volume_factor': 5000,
                'min_days': 1,
                'max_days': 2
            },
            {
                'name': 'J&T Regular',
                'code': 'jnt_reg',
                'base_price': 12000,
                'price_per_kg': 7000,
                'price_per_km': 0.4,
                'volume_factor': 6000,
                'min_days': 2,
                'max_days': 5
            },
            {
                'name': 'SiCepat Regular',
                'code': 'sicepat_reg',
                'base_price': 14000,
                'price_per_kg': 7500,
                'price_per_km': 0.45,
                'volume_factor': 5500,
                'min_days': 2,
                'max_days': 4
            },
            {
                'name': 'Pos Indonesia',
                'code': 'pos_reg',
                'base_price': 10000,
                'price_per_kg': 6000,
                'price_per_km': 0.3,
                'volume_factor': 7000,
                'min_days': 3,
                'max_days': 7
            }
        ]

        for service_data in shipping_data:
            existing = ShippingService.query.filter_by(code=service_data['code']).first()
            if not existing:
                service = ShippingService(
                    name=service_data['name'],
                    code=service_data['code'],
                    base_price=service_data['base_price'],
                    price_per_kg=service_data['price_per_kg'],
                    price_per_km=service_data['price_per_km'],
                    volume_factor=service_data['volume_factor'],
                    min_days=service_data['min_days'],
                    max_days=service_data['max_days'],
                    is_active=True
                )
                db.session.add(service)

        # Create products
        products = [
            # Gitar
            {
                'name': 'Yamaha F310 Acoustic Guitar',
                'description': 'Gitar akustik entry-level dengan kualitas suara yang jernih dan build quality yang solid. Cocok untuk pemula hingga intermediate.',
                'price': 1850000,
                'stock_quantity': 15,
                'minimum_stock': 3,
                'low_stock_threshold': 8,
                'brand': 'Yamaha',
                'model': 'F310',
                'category_id': category_objects[0].id if len(category_objects) > 0 else 1,
                'supplier_id': supplier_objects[0].id if len(supplier_objects) > 0 else None,
                'is_featured': True,
                'is_active': True,
                'image_url': 'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=500',
                'weight': 2200, 'length': 104, 'width': 38, 'height': 12
            },
            {
                'name': 'Fender Player Stratocaster',
                'description': 'Gitar elektrik legendaris dengan tone versatile dan playability yang luar biasa. Dilengkapi pickup single-coil yang iconic.',
                'price': 12500000,
                'stock_quantity': 8,
                'minimum_stock': 2,
                'low_stock_threshold': 5,
                'brand': 'Fender',
                'model': 'Player Stratocaster',
                'category_id': category_objects[0].id if len(category_objects) > 0 else 1,
                'supplier_id': supplier_objects[1].id if len(supplier_objects) > 1 else None,
                'is_featured': True,
                'is_active': True,
                'image_url': 'https://images.unsplash.com/photo-1564186763535-ebb21ef5277f?w=500',
                'weight': 3500, 'length': 99, 'width': 32, 'height': 5
            },
            # Bass
            {
                'name': 'Fender Player Jazz Bass',
                'description': 'Bass elektrik dengan tone yang punchy dan artikulasi yang jelas. Ideal untuk berbagai genre musik.',
                'price': 8750000,
                'stock_quantity': 6,
                'minimum_stock': 2,
                'low_stock_threshold': 4,
                'brand': 'Fender',
                'model': 'Player Jazz Bass',
                'category_id': category_objects[1].id if len(category_objects) > 1 else 1,
                'supplier_id': supplier_objects[1].id if len(supplier_objects) > 1 else None,
                'is_featured': True,
                'is_active': True,
                'image_url': 'https://images.unsplash.com/photo-1520637836862-4d197d17c2a2?w=500',
                'weight': 4200, 'length': 116, 'width': 36, 'height': 6
            },
            # Drum
            {
                'name': 'Pearl Export Series Drum Kit',
                'description': 'Set drum lengkap 5-piece dengan hardware dan cymbal. Suara yang powerful dan punch untuk berbagai genre.',
                'price': 8750000,
                'stock_quantity': 4,
                'minimum_stock': 1,
                'low_stock_threshold': 3,
                'brand': 'Pearl',
                'model': 'Export Series',
                'category_id': category_objects[2].id if len(category_objects) > 2 else 1,
                'supplier_id': supplier_objects[2].id if len(supplier_objects) > 2 else None,
                'is_featured': True,
                'is_active': True,
                'image_url': 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=500',
                'weight': 35000, 'length': 150, 'width': 120, 'height': 80
            },
            # Keyboard
            {
                'name': 'Yamaha PSR-E373 Keyboard',
                'description': 'Keyboard 61-key dengan 622 suara dan 205 style. Touch response dan learning function untuk pemula.',
                'price': 2750000,
                'stock_quantity': 12,
                'minimum_stock': 3,
                'low_stock_threshold': 8,
                'brand': 'Yamaha',
                'model': 'PSR-E373',
                'category_id': category_objects[3].id if len(category_objects) > 3 else 1,
                'supplier_id': supplier_objects[0].id if len(supplier_objects) > 0 else None,
                'is_featured': True,
                'is_active': True,
                'image_url': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=500',
                'weight': 4500, 'length': 94, 'width': 31, 'height': 10
            },
            {
                'name': 'Roland FP-30X Digital Piano',
                'description': 'Piano digital premium dengan SuperNATURAL Piano sound dan PHA-4 Standard keyboard untuk feel yang authentic.',
                'price': 9850000,
                'stock_quantity': 5,
                'minimum_stock': 2,
                'low_stock_threshold': 4,
                'brand': 'Roland',
                'model': 'FP-30X',
                'category_id': category_objects[3].id if len(category_objects) > 3 else 1,
                'supplier_id': supplier_objects[0].id if len(supplier_objects) > 0 else None,
                'is_featured': True,
                'is_active': True,
                'image_url': 'https://images.unsplash.com/photo-1549298327-ffb31f3a7249?w=500',
                'weight': 16500, 'length': 130, 'width': 28, 'height': 15
            },
            # Sound System
            {
                'name': 'Yamaha DXR10 Active Speaker',
                'description': 'Speaker aktif 10 inch dengan DSP built-in. Suara yang jernih dan powerful untuk live performance.',
                'price': 6750000,
                'stock_quantity': 8,
                'minimum_stock': 2,
                'low_stock_threshold': 5,
                'brand': 'Yamaha',
                'model': 'DXR10',
                'category_id': category_objects[4].id if len(category_objects) > 4 else 1,
                'supplier_id': supplier_objects[0].id if len(supplier_objects) > 0 else None,
                'is_featured': True,
                'is_active': True,
                'image_url': 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=500',
                'weight': 18500, 'length': 60, 'width': 40, 'height': 35
            },
            # Aksesoris
            {
                'name': 'Audio-Technica ATH-M50x Headphones',
                'description': 'Headphone monitoring profesional dengan sound signature yang balanced dan build quality yang robust.',
                'price': 1850000,
                'stock_quantity': 20,
                'minimum_stock': 5,
                'low_stock_threshold': 12,
                'brand': 'Audio-Technica',
                'model': 'ATH-M50x',
                'category_id': category_objects[5].id if len(category_objects) > 5 else 1,
                'supplier_id': supplier_objects[3].id if len(supplier_objects) > 3 else None,
                'is_featured': True,
                'is_active': True,
                'image_url': 'https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=500',
                'weight': 285, 'length': 20, 'width': 18, 'height': 8
            },
            {
                'name': 'Shure SM58 Dynamic Microphone',
                'description': 'Mikrofon dinamis legendaris untuk vokal live dan recording. Durability dan clarity yang terjamin.',
                'price': 1650000,
                'stock_quantity': 15,
                'minimum_stock': 3,
                'low_stock_threshold': 8,
                'brand': 'Shure',
                'model': 'SM58',
                'category_id': category_objects[5].id if len(category_objects) > 5 else 1,
                'supplier_id': supplier_objects[4].id if len(supplier_objects) > 4 else None,
                'is_featured': True,
                'is_active': True,
                'image_url': 'https://images.unsplash.com/photo-15907369955-71cc94901144?w=500',
                'weight': 298, 'length': 16, 'width': 5, 'height': 5
            },
            {
                'name': 'Boss DS-1 Distortion Pedal',
                'description': 'Pedal distortion klasik dengan tone yang aggressive dan sustain yang smooth. Essential untuk rock dan metal.',
                'price': 1250000,
                'stock_quantity': 2,
                'minimum_stock': 3,
                'low_stock_threshold': 8,
                'brand': 'Boss',
                'model': 'DS-1',
                'category_id': category_objects[5].id if len(category_objects) > 5 else 1,
                'supplier_id': supplier_objects[3].id if len(supplier_objects) > 3 else None,
                'is_featured': False,
                'is_active': True,
                'image_url': 'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=500',
                'weight': 400, 'length': 12, 'width': 7, 'height': 6
            }
        ]

        products_created = 0
        for product_data in products:
            existing = Product.query.filter_by(name=product_data['name']).first()
            if not existing:
                product = Product(
                    name=product_data['name'],
                    description=product_data['description'],
                    price=product_data['price'],
                    stock_quantity=product_data['stock_quantity'],
                    minimum_stock=product_data['minimum_stock'],
                    low_stock_threshold=product_data['low_stock_threshold'],
                    brand=product_data['brand'],
                    model=product_data['model'],
                    category_id=product_data['category_id'],
                    supplier_id=product_data['supplier_id'],
                    is_featured=product_data['is_featured'],
                    is_active=product_data['is_active'],
                    image_url=product_data['image_url'],
                    weight=product_data.get('weight'),
                    length=product_data.get('length'),
                    width=product_data.get('width'),
                    height=product_data.get('height')
                )
                db.session.add(product)
                products_created += 1

        db.session.commit()
        print(f"Sample data created successfully!")
        print(f"Created {len(categories_data)} categories, {products_created} new products, {len(shipping_data)} shipping services, and {len(suppliers_data)} suppliers")

if __name__ == '__main__':
    create_sample_data()