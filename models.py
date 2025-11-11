from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import String, Text, Numeric, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
import pytz
import re
import unicodedata

# Import db instance from database module
from database import db

# Jakarta/WIB Timezone (UTC+7)
WIB_TIMEZONE = pytz.timezone('Asia/Jakarta')

def get_wib_time():
    """Get current time in WIB timezone (UTC+7) as timezone-aware datetime"""
    return datetime.now(WIB_TIMEZONE)

def get_utc_time():
    """Get current time in UTC for database storage (timezone-aware)"""
    return datetime.now(pytz.UTC)

def slugify(text):
    """Convert text to URL-friendly slug"""
    text = str(text).lower()
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(Integer, primary_key=True)
    email = db.Column(String(120), unique=True, nullable=False)
    password_hash = db.Column(String(255), nullable=False)
    name = db.Column(String(100), nullable=False)
    phone = db.Column(String(20))
    address = db.Column(Text)
    active = db.Column(Boolean, default=True)
    role = db.Column(String(20), default='buyer')  # admin, staff, buyer
    created_at = db.Column(DateTime, default=get_utc_time)

    # Relationships
    cart_items = relationship('CartItem', backref='user', lazy=True, cascade='all, delete-orphan')
    orders = relationship('Order', foreign_keys='Order.user_id', backref='user', lazy=True)

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_staff(self):
        return self.role == 'staff'

    @property
    def is_buyer(self):
        return self.role == 'buyer'

    def __repr__(self):
        return f'<User {self.email}>'

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(100), nullable=False)
    description = db.Column(Text)
    image_url = db.Column(String(255))
    is_active = db.Column(Boolean, default=True)
    created_at = db.Column(DateTime, default=get_utc_time)

    # Relationships
    products = relationship('Product', backref='category', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(200), nullable=False)
    slug = db.Column(String(255), unique=True, nullable=True)
    gtin = db.Column(String(100), unique=True, nullable=True)  # GTIN/Barcode
    description = db.Column(Text)
    price = db.Column(Numeric(10, 2), nullable=False)
    stock_quantity = db.Column(Integer, default=0)
    image_url = db.Column(String(255))  # Main thumbnail image
    brand = db.Column(String(100))
    model = db.Column(String(100))
    is_active = db.Column(Boolean, default=True)
    is_featured = db.Column(Boolean, default=False)
    category_id = db.Column(Integer, ForeignKey('categories.id'), nullable=False)
    created_at = db.Column(DateTime, default=get_utc_time)

    # Informasi supplier dan dimensi untuk shipping
    supplier_id = db.Column(Integer, ForeignKey('suppliers.id'), nullable=True)
    weight = db.Column(Numeric(8, 2), default=0)  # dalam gram
    shipping_weight = db.Column(Numeric(8, 2), default=0)  # berat setelah packing (gram)
    length = db.Column(Numeric(8, 2), default=0)  # dalam cm
    width = db.Column(Numeric(8, 2), default=0)   # dalam cm
    height = db.Column(Numeric(8, 2), default=0)  # dalam cm

    # Stock management
    minimum_stock = db.Column(Integer, default=5)  # Minimum stock threshold
    low_stock_threshold = db.Column(Integer, default=10)  # Warning threshold

    # Relationships
    cart_items = relationship('CartItem', backref='product', lazy=True)
    order_items = relationship('OrderItem', backref='product', lazy=True)
    images = relationship('ProductImage', backref='product', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Product {self.name}>'

    @property
    def volume_cm3(self):
        """Menghitung volume produk dalam cm3"""
        return float(self.length or 0) * float(self.width or 0) * float(self.height or 0)

    @property
    def formatted_price(self):
        return f"Rp {self.price:,.0f}".replace(',', '.')

    @property
    def stock_status(self):
        """Return stock status: critical, low, adequate, or out_of_stock"""
        if self.stock_quantity <= 0:
            return 'out_of_stock'
        elif self.stock_quantity <= self.minimum_stock:
            return 'critical'
        elif self.stock_quantity <= self.low_stock_threshold:
            return 'low'
        else:
            return 'adequate'

    @property
    def stock_status_color(self):
        """Return Bootstrap color class for stock status"""
        status_colors = {
            'out_of_stock': 'danger',
            'critical': 'danger',
            'low': 'warning',
            'adequate': 'success'
        }
        return status_colors.get(self.stock_status, 'secondary')

    @property
    def needs_restock(self):
        """Check if product needs restock"""
        return self.stock_quantity <= self.minimum_stock

    def generate_slug(self):
        """Generate unique slug from product name"""
        if not self.name:
            return None

        base_slug = slugify(self.name)
        slug = base_slug
        counter = 1

        while Product.query.filter(Product.slug == slug, Product.id != self.id).first():
            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug
    
    def generate_gtin(self):
        """Generate GTIN with format hrtbrg+timestamp if not provided"""
        if not self.gtin:
            import time
            timestamp = str(int(time.time() * 1000))  # milliseconds timestamp
            return f"hrtbrg{timestamp}"
        return self.gtin

    def ensure_slug(self):
        """Ensure product has a slug, generate if missing"""
        if not self.slug:
            from slugify import slugify
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            # Check for existing slugs and make unique
            while Product.query.filter_by(slug=slug).first():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

    @property
    def seo_title(self):
        """Generate SEO-friendly title"""
        title = self.name
        if self.brand:
            title += f" - {self.brand}"
        title += " | Hurtrock Music Store"
        return title

    @property
    def seo_description(self):
        """Generate SEO-friendly description"""
        if self.description:
            desc = self.description[:150]
            if len(self.description) > 150:
                desc += "..."
        else:
            desc = f"{self.name}"
            if self.brand:
                desc += f" dari {self.brand}"
            desc += f" tersedia di Hurtrock Music Store. Harga: {self.formatted_price}. Kualitas terjamin, pengiriman cepat."
        return desc

    @property
    def seo_keywords(self):
        """Generate SEO keywords"""
        keywords = [self.name]
        if self.brand:
            keywords.append(self.brand)
        if self.model:
            keywords.append(self.model)
        if self.category:
            keywords.append(self.category.name)
        keywords.extend(['alat musik', 'music store', 'toko musik', 'hurtrock'])
        return ', '.join(keywords)

    def to_dict(self):
        """Convert product to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'price': float(self.price),
            'image_url': self.image_url or '/static/images/placeholder.jpg',
            'brand': self.brand or '',
            'description': self.description or '',
            'category': self.category.name if self.category else '',
            'is_active': self.is_active,
            'images': [{'url': img.image_url, 'is_thumbnail': img.is_thumbnail} for img in self.images]
        }

class ProductImage(db.Model):
    __tablename__ = 'product_images'

    id = db.Column(Integer, primary_key=True)
    product_id = db.Column(Integer, ForeignKey('products.id'), nullable=False)
    image_url = db.Column(String(255), nullable=False)
    is_thumbnail = db.Column(Boolean, default=False)  # True if this is the main thumbnail
    display_order = db.Column(Integer, default=0)  # Order for displaying images
    created_at = db.Column(DateTime, default=get_utc_time)

    def __repr__(self):
        return f'<ProductImage {self.product_id}:{self.image_url}>'

class CartItem(db.Model):
    __tablename__ = 'cart_items'

    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer, ForeignKey('users.id'), nullable=False)
    product_id = db.Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = db.Column(Integer, nullable=False, default=1)
    created_at = db.Column(DateTime, default=get_utc_time)

    def __repr__(self):
        return f'<CartItem User:{self.user_id} Product:{self.product_id}>'

    @property
    def subtotal(self):
        return self.quantity * self.product.price

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer, ForeignKey('users.id'), nullable=False)
    total_amount = db.Column(Numeric(10, 2), nullable=False)
    status = db.Column(String(50), default='pending')  # pending, paid, shipped, delivered, cancelled
    tracking_number = db.Column(String(100))  # For package tracking
    courier_service = db.Column(String(50))  # JNE, J&T, SiCepat, etc.
    shipping_service_id = db.Column(Integer, ForeignKey('shipping_services.id'), nullable=True)
    shipping_cost = db.Column(Numeric(10, 2), default=0)
    shipping_address = db.Column(Text)
    payment_method = db.Column(String(50))  # cash, debit, qris, transfer, ewallet, credit_card, other
    estimated_delivery_days = db.Column(Integer, default=0)

    # Kasir/POS fields
    source_type = db.Column(String(20), default='online')  # 'online' (web/marketplace) or 'offline' (kasir/POS)
    buyer_name = db.Column(String(200))  # Nama pembeli untuk transaksi kasir offline
    pos_user_id = db.Column(Integer, ForeignKey('users.id'), nullable=True)  # Staff kasir yang melayani
    paid_at = db.Column(DateTime)  # Waktu pembayaran diterima
    local_transaction_id = db.Column(String(100))  # ID dari sistem offline untuk idempotency

    created_at = db.Column(DateTime, default=get_utc_time)
    updated_at = db.Column(DateTime, default=get_utc_time, onupdate=get_utc_time)

    # Relationships
    order_items = relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    pos_user = relationship('User', foreign_keys=[pos_user_id], backref='pos_orders', lazy=True)

    def __repr__(self):
        return f'<Order {self.id}>'

    @property
    def formatted_total(self):
        return f"Rp {self.total_amount:,.0f}".replace(',', '.')

class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(Integer, primary_key=True)
    order_id = db.Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = db.Column(Integer, nullable=False)
    price = db.Column(Numeric(10, 2), nullable=False)  # Price at time of order

    def __repr__(self):
        return f'<OrderItem Order:{self.order_id} Product:{self.product_id}>'

    @property
    def subtotal(self):
        return self.quantity * self.price

    @property
    def formatted_subtotal(self):
        return f"Rp {self.subtotal:,.0f}".replace(',', '.')


class Invoice(db.Model):
    __tablename__ = 'invoices'
    
    id = db.Column(Integer, primary_key=True)
    invoice_number = db.Column(String(50), unique=True, nullable=False)
    order_id = db.Column(Integer, ForeignKey('orders.id'), nullable=True)
    customer_name = db.Column(String(200), nullable=False)
    customer_email = db.Column(String(120))
    customer_phone = db.Column(String(20))
    customer_address = db.Column(Text)
    subtotal = db.Column(Numeric(10, 2), nullable=False)
    tax_amount = db.Column(Numeric(10, 2), default=0)
    discount_amount = db.Column(Numeric(10, 2), default=0)
    shipping_cost = db.Column(Numeric(10, 2), default=0)
    total_amount = db.Column(Numeric(10, 2), nullable=False)
    status = db.Column(String(20), default='Pending')  # Paid, Pending, On Process
    payment_method = db.Column(String(50))
    notes = db.Column(Text)
    created_at = db.Column(DateTime, default=get_utc_time)
    updated_at = db.Column(DateTime, default=get_utc_time, onupdate=get_utc_time)
    issued_by = db.Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Relationships
    order = relationship('Order', backref='invoices', lazy=True)
    issuer = relationship('User', foreign_keys=[issued_by], backref='issued_invoices', lazy=True)
    items = relationship('InvoiceItem', backref='invoice', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Invoice {self.invoice_number}>'
    
    @property
    def formatted_total(self):
        return f"Rp {self.total_amount:,.0f}".replace(',', '.')
    
    def generate_invoice_number(self):
        """Generate unique invoice number with format INV-YYYYMMDD-XXXX"""
        if not self.invoice_number:
            from datetime import datetime
            today = datetime.now().strftime('%Y%m%d')
            # Find last invoice number for today
            last_invoice = Invoice.query.filter(
                Invoice.invoice_number.like(f'INV-{today}-%')
            ).order_by(Invoice.id.desc()).first()
            
            if last_invoice:
                last_num = int(last_invoice.invoice_number.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            
            self.invoice_number = f'INV-{today}-{new_num:04d}'
        return self.invoice_number


class InvoiceItem(db.Model):
    __tablename__ = 'invoice_items'
    
    id = db.Column(Integer, primary_key=True)
    invoice_id = db.Column(Integer, ForeignKey('invoices.id'), nullable=False)
    item_name = db.Column(String(200), nullable=False)
    description = db.Column(Text)
    quantity = db.Column(Integer, nullable=False)
    unit_price = db.Column(Numeric(10, 2), nullable=False)
    
    def __repr__(self):
        return f'<InvoiceItem {self.item_name}>'
    
    @property
    def subtotal(self):
        return self.quantity * self.unit_price
    
    @property
    def formatted_subtotal(self):
        return f"Rp {self.subtotal:,.0f}".replace(',', '.')


class Supplier(db.Model):
    __tablename__ = 'suppliers'

    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(200), nullable=False)
    contact_person = db.Column(String(100))
    email = db.Column(String(120))
    phone = db.Column(String(20))
    address = db.Column(Text)
    company = db.Column(String(200))
    notes = db.Column(Text)
    is_active = db.Column(Boolean, default=True)
    created_at = db.Column(DateTime, default=get_utc_time)

    # Relationships
    products = relationship('Product', backref='supplier', lazy=True)

    def __repr__(self):
        return f'<Supplier {self.name}>'

class ShippingService(db.Model):
    __tablename__ = 'shipping_services'

    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(100), nullable=False)  # JNE, JNT, SiCepat, etc
    code = db.Column(String(20), unique=True, nullable=False)  # jne, jnt, sicepat
    base_price = db.Column(Numeric(10, 2), nullable=False)  # Harga dasar per kg
    price_per_kg = db.Column(Numeric(10, 2), nullable=False)  # Harga tambahan per kg
    price_per_km = db.Column(Numeric(8, 4), default=0)  # Harga per km jarak
    volume_factor = db.Column(Numeric(8, 4), default=5000)  # Faktor volume divider (cm3 to kg)
    min_days = db.Column(Integer, default=1)  # Estimasi minimum hari
    max_days = db.Column(Integer, default=3)  # Estimasi maksimum hari
    is_active = db.Column(Boolean, default=True)
    created_at = db.Column(DateTime, default=get_utc_time)

    # Relationships
    orders = relationship('Order', backref='shipping_service', lazy=True)

    def __repr__(self):
        return f'<ShippingService {self.name}>'

    def calculate_shipping_cost(self, weight_gram, volume_cm3, distance_km=50):
        """
        Menghitung biaya shipping berdasarkan berat, volume, dan jarak
        """
        # Convert gram to kg
        weight_kg = float(weight_gram) / 1000

        # Calculate volumetric weight
        volumetric_weight_kg = float(volume_cm3) / float(self.volume_factor)

        # Use the higher weight (actual or volumetric)
        billable_weight = max(weight_kg, volumetric_weight_kg)

        # Calculate cost
        base_cost = float(self.base_price)
        weight_cost = billable_weight * float(self.price_per_kg)
        distance_cost = float(distance_km) * float(self.price_per_km)

        total_cost = base_cost + weight_cost + distance_cost

        return round(total_cost, 2)

class RestockOrder(db.Model):
    __tablename__ = 'restock_orders'

    id = db.Column(Integer, primary_key=True)
    supplier_id = db.Column(Integer, ForeignKey('suppliers.id'), nullable=False)
    status = db.Column(String(50), default='pending')  # pending, ordered, received, cancelled
    total_amount = db.Column(Numeric(12, 2), default=0)
    notes = db.Column(Text)
    order_date = db.Column(DateTime, default=datetime.utcnow)
    expected_date = db.Column(DateTime)
    received_date = db.Column(DateTime)
    created_by = db.Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = db.Column(DateTime, default=get_utc_time)

    # Relationships
    supplier = relationship('Supplier', backref='restock_orders', lazy=True)
    created_by_user = relationship('User', backref='created_restock_orders', lazy=True)
    items = relationship('RestockOrderItem', backref='restock_order', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<RestockOrder {self.id}>'

    @property
    def formatted_total(self):
        return f"Rp {self.total_amount:,.0f}".replace(',', '.')

class RestockOrderItem(db.Model):
    __tablename__ = 'restock_order_items'

    id = db.Column(Integer, primary_key=True)
    restock_order_id = db.Column(Integer, ForeignKey('restock_orders.id'), nullable=False)
    product_id = db.Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity_ordered = db.Column(Integer, nullable=False)
    quantity_received = db.Column(Integer, default=0)
    unit_cost = db.Column(Numeric(10, 2), nullable=False)

    # Relationships
    product = relationship('Product', backref='restock_items', lazy=True)

    def __repr__(self):
        return f'<RestockOrderItem {self.id}>'

    @property
    def subtotal(self):
        return self.quantity_ordered * self.unit_cost

    @property
    def formatted_subtotal(self):
        return f"Rp {self.subtotal:,.0f}".replace(',', '.')

class PaymentConfiguration(db.Model):
    __tablename__ = 'payment_configurations'

    id = db.Column(Integer, primary_key=True)
    provider = db.Column(String(50), nullable=False)  # 'stripe', 'midtrans', 'xendit', 'doku'
    is_active = db.Column(Boolean, default=False)
    is_sandbox = db.Column(Boolean, default=True)

    # Midtrans specific
    midtrans_client_key = db.Column(String(255))
    midtrans_server_key = db.Column(String(255))
    midtrans_merchant_id = db.Column(String(100))

    # Stripe specific  
    stripe_publishable_key = db.Column(String(255))
    stripe_secret_key = db.Column(String(255))

    # Xendit specific
    xendit_api_key = db.Column(String(255))
    xendit_webhook_token = db.Column(String(255))
    xendit_public_key = db.Column(String(255))

    # DOKU specific
    doku_client_id = db.Column(String(255))
    doku_secret_key = db.Column(String(255))
    doku_private_key = db.Column(Text)  # RSA private key for DOKU
    doku_public_key = db.Column(Text)   # DOKU public key for verification

    # Callback URLs
    callback_finish_url = db.Column(String(255))
    callback_unfinish_url = db.Column(String(255))
    callback_error_url = db.Column(String(255))
    notification_url = db.Column(String(255))

    # Additional callback URLs untuk Midtrans
    recurring_notification_url = db.Column(String(255))
    account_linking_url = db.Column(String(255))

    created_at = db.Column(DateTime, default=get_utc_time)
    updated_at = db.Column(DateTime, default=get_utc_time, onupdate=get_utc_time)

    def __repr__(self):
        return f'<PaymentConfiguration {self.provider}>'

class MidtransTransaction(db.Model):
    __tablename__ = 'midtrans_transactions'

    id = db.Column(Integer, primary_key=True)
    order_id = db.Column(Integer, ForeignKey('orders.id'), nullable=False)
    transaction_id = db.Column(String(100), unique=True, nullable=False)
    gross_amount = db.Column(Numeric(10, 2), nullable=False)
    payment_type = db.Column(String(50))
    transaction_status = db.Column(String(50))
    fraud_status = db.Column(String(50))
    settlement_time = db.Column(DateTime)

    # Midtrans response data
    snap_token = db.Column(String(255))
    snap_redirect_url = db.Column(String(500))
    midtrans_response = db.Column(Text)  # JSON response from Midtrans

    created_at = db.Column(DateTime, default=get_utc_time)
    updated_at = db.Column(DateTime, default=get_utc_time, onupdate=get_utc_time)

    # Relationships
    order = relationship('Order', backref='midtrans_transactions', lazy=True)

    def __repr__(self):
        return f'<MidtransTransaction {self.transaction_id}>'

class XenditTransaction(db.Model):
    __tablename__ = 'xendit_transactions'

    id = db.Column(Integer, primary_key=True)
    order_id = db.Column(Integer, ForeignKey('orders.id'), nullable=False)
    transaction_id = db.Column(String(100), unique=True, nullable=False)
    external_id = db.Column(String(100), nullable=False)
    amount = db.Column(Numeric(10, 2), nullable=False)

    # Payment method details
    payment_method = db.Column(String(50))  # 'Ewallet', 'VIRTUAL_ACCOUNT', 'QR_CODE', 'INVOICE'
    channel_code = db.Column(String(50))    # 'OVO', 'DANA', 'LINKAJA', 'SHOPEEPAY', etc.

    # Transaction status
    status = db.Column(String(50))          # 'PENDING', 'SUCCEEDED', 'FAILED', 'EXPIRED'

    # Payment URLs and details
    checkout_url = db.Column(String(500))
    mobile_deeplink = db.Column(String(500))
    qr_code = db.Column(String(500))

    # Virtual account details (if applicable)
    va_number = db.Column(String(50))
    bank_code = db.Column(String(10))

    # Timestamps
    created_at = db.Column(DateTime, default=get_utc_time)
    updated_at = db.Column(DateTime, default=get_utc_time, onupdate=get_utc_time)
    expired_at = db.Column(DateTime)
    paid_at = db.Column(DateTime)

    # Store full response from Xendit
    xendit_response = db.Column(Text)

    # Relationships
    order = relationship('Order', backref='xendit_transactions', lazy=True)

    def __repr__(self):
        return f'<XenditTransaction {self.transaction_id}>'

class DokuTransaction(db.Model):
    __tablename__ = 'doku_transactions'

    id = db.Column(Integer, primary_key=True)
    order_id = db.Column(Integer, ForeignKey('orders.id'), nullable=False)
    transaction_id = db.Column(String(100), unique=True, nullable=False)
    invoice_number = db.Column(String(100), nullable=False)
    amount = db.Column(Numeric(10, 2), nullable=False)

    # Payment method details  
    payment_method = db.Column(String(50))  # 'VIRTUAL_ACCOUNT', 'DIRECT_DEBIT', 'CREDIT_CARD'
    channel_code = db.Column(String(50))    # 'VIRTUAL_ACCOUNT_BNI', 'VIRTUAL_ACCOUNT_MANDIRI', etc.

    # Transaction status
    status = db.Column(String(50))          # 'PENDING', 'SUCCESS', 'FAILED', 'EXPIRED'

    # Virtual account details (if applicable)
    va_number = db.Column(String(50))
    bank_code = db.Column(String(10))

    # Payment URLs
    checkout_url = db.Column(String(500))

    # Timestamps
    created_at = db.Column(DateTime, default=get_utc_time)
    updated_at = db.Column(DateTime, default=get_utc_time, onupdate=get_utc_time)
    expired_at = db.Column(DateTime)
    paid_at = db.Column(DateTime)

    # Store full response from DOKU
    doku_response = db.Column(Text)

    # Relationships
    order = relationship('Order', backref='doku_transactions', lazy=True)

    def __repr__(self):
        return f'<DokuTransaction {self.transaction_id}>'

class OfflineTransaction(db.Model):
    __tablename__ = 'offline_transactions'

    id = db.Column(Integer, primary_key=True)
    local_transaction_id = db.Column(String(100), unique=True, nullable=False)  # UUID from local storage
    cashier_user_id = db.Column(Integer, ForeignKey('users.id'), nullable=False)

    # Transaction details
    subtotal = db.Column(Numeric(10, 2), nullable=False)
    tax_amount = db.Column(Numeric(10, 2), default=0)
    discount_amount = db.Column(Numeric(10, 2), default=0)
    total_amount = db.Column(Numeric(10, 2), nullable=False)

    # Payment information
    payment_method = db.Column(String(50), nullable=False)  # 'cash', 'card', 'transfer'
    payment_amount = db.Column(Numeric(10, 2), nullable=False)
    change_amount = db.Column(Numeric(10, 2), default=0)

    # Customer information (optional)
    customer_name = db.Column(String(200))
    customer_phone = db.Column(String(20))
    customer_email = db.Column(String(120))

    # Sync status
    sync_status = db.Column(String(20), default='pending')  # 'pending', 'synced', 'failed'
    sync_attempts = db.Column(Integer, default=0)
    last_sync_attempt = db.Column(DateTime)
    sync_error_message = db.Column(Text)

    # Timestamps
    transaction_date = db.Column(DateTime, nullable=False)  # When transaction was made offline
    created_at = db.Column(DateTime, default=get_utc_time)
    synced_at = db.Column(DateTime)

    # Store original offline data for debugging
    offline_data = db.Column(Text)  # JSON of original offline transaction

    # Relationships
    cashier = relationship('User', backref='offline_transactions', lazy=True)
    offline_items = relationship('OfflineTransactionItem', backref='offline_transaction', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<OfflineTransaction {self.local_transaction_id}>'

    @property
    def formatted_total(self):
        return f"Rp {self.total_amount:,.0f}".replace(',', '.')

    def to_dict(self):
        return {
            'id': self.id,
            'local_transaction_id': self.local_transaction_id,
            'cashier_user_id': self.cashier_user_id,
            'subtotal': float(self.subtotal),
            'tax_amount': float(self.tax_amount),
            'discount_amount': float(self.discount_amount),
            'total_amount': float(self.total_amount),
            'payment_method': self.payment_method,
            'payment_amount': float(self.payment_amount),
            'change_amount': float(self.change_amount),
            'customer_name': self.customer_name,
            'customer_phone': self.customer_phone,
            'customer_email': self.customer_email,
            'sync_status': self.sync_status,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'items': [item.to_dict() for item in self.offline_items]
        }

class OfflineTransactionItem(db.Model):
    __tablename__ = 'offline_transaction_items'

    id = db.Column(Integer, primary_key=True)
    offline_transaction_id = db.Column(Integer, ForeignKey('offline_transactions.id'), nullable=False)
    product_id = db.Column(Integer, ForeignKey('products.id'), nullable=False)

    # Product details at time of sale (for price history)
    product_name = db.Column(String(200), nullable=False)
    product_price = db.Column(Numeric(10, 2), nullable=False)
    quantity = db.Column(Integer, nullable=False)
    subtotal = db.Column(Numeric(10, 2), nullable=False)

    # Discount on this item
    discount_percent = db.Column(Numeric(5, 2), default=0)
    discount_amount = db.Column(Numeric(10, 2), default=0)

    # Stock tracking
    stock_reduced = db.Column(Boolean, default=False)  # Track if stock has been reduced during sync

    # Relationships
    product = relationship('Product', backref='offline_transaction_items', lazy=True)

    def __repr__(self):
        return f'<OfflineTransactionItem {self.product_name}>'

    @property
    def formatted_subtotal(self):
        return f"Rp {self.subtotal:,.0f}".replace(',', '.')

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'product_price': float(self.product_price),
            'quantity': self.quantity,
            'subtotal': float(self.subtotal),
            'discount_percent': float(self.discount_percent) if self.discount_percent else 0,
            'discount_amount': float(self.discount_amount) if self.discount_amount else 0,
            'stock_reduced': self.stock_reduced
        }

class CashierSession(db.Model):
    __tablename__ = 'cashier_sessions'

    id = db.Column(Integer, primary_key=True)
    cashier_user_id = db.Column(Integer, ForeignKey('users.id'), nullable=False)
    session_start = db.Column(DateTime, default=get_utc_time)
    session_end = db.Column(DateTime)

    # Cash drawer tracking
    opening_cash = db.Column(Numeric(10, 2), default=0)
    closing_cash = db.Column(Numeric(10, 2))
    expected_cash = db.Column(Numeric(10, 2))
    cash_difference = db.Column(Numeric(10, 2))

    # Transaction summary
    total_transactions = db.Column(Integer, default=0)
    total_sales = db.Column(Numeric(10, 2), default=0)
    cash_sales = db.Column(Numeric(10, 2), default=0)
    card_sales = db.Column(Numeric(10, 2), default=0)

    # Session status
    status = db.Column(String(20), default='active')  # 'active', 'closed', 'suspended'
    notes = db.Column(Text)

    # Relationships
    cashier = relationship('User', backref='cashier_sessions', lazy=True)

    def __repr__(self):
        return f'<CashierSession {self.cashier.username} - {self.session_start}>'

    @property
    def session_duration(self):
        if self.session_end:
            return self.session_end - self.session_start
        return datetime.utcnow() - self.session_start

    def to_dict(self):
        return {
            'id': self.id,
            'cashier_user_id': self.cashier_user_id,
            'cashier_name': self.cashier.name,
            'session_start': self.session_start.isoformat() if self.session_start else None,
            'session_end': self.session_end.isoformat() if self.session_end else None,
            'opening_cash': float(self.opening_cash) if self.opening_cash else 0,
            'closing_cash': float(self.closing_cash) if self.closing_cash else None,
            'expected_cash': float(self.expected_cash) if self.expected_cash else None,
            'cash_difference': float(self.cash_difference) if self.cash_difference else None,
            'total_transactions': self.total_transactions,
            'total_sales': float(self.total_sales) if self.total_sales else 0,
            'cash_sales': float(self.cash_sales) if self.cash_sales else 0,
            'card_sales': float(self.card_sales) if self.card_sales else 0,
            'status': self.status,
            'notes': self.notes
        }

class StoreProfile(db.Model):
    __tablename__ = 'store_profiles'

    id = db.Column(Integer, primary_key=True)
    store_name = db.Column(String(200), nullable=False, default='Hurtrock Music Store')
    store_tagline = db.Column(String(255), default='Toko Alat Musik Terpercaya')
    store_address = db.Column(Text, nullable=False)
    store_city = db.Column(String(100), nullable=False)
    store_postal_code = db.Column(String(10))
    store_phone = db.Column(String(20), nullable=False)
    store_email = db.Column(String(120), nullable=False)
    store_website = db.Column(String(255))
    store_description = db.Column(Text)  # About/description field

    # Branch information
    branch_name = db.Column(String(200))
    branch_code = db.Column(String(10))
    branch_manager = db.Column(String(100))

    # Business information
    business_license = db.Column(String(100))
    tax_number = db.Column(String(50))

    # Logo and branding
    logo_url = db.Column(String(255))
    primary_color = db.Column(String(7), default='#FF6B35')  # Hex color
    secondary_color = db.Column(String(7), default='#FF8C42')  # Hex color

    # Operating hours
    operating_hours = db.Column(Text)  # JSON format for flexible hours

    # Social media
    facebook_url = db.Column(String(255))
    instagram_url = db.Column(String(255))
    whatsapp_number = db.Column(String(20))

    # Settings
    is_active = db.Column(Boolean, default=True)
    created_at = db.Column(DateTime, default=get_utc_time)
    updated_at = db.Column(DateTime, default=get_utc_time, onupdate=get_utc_time)

    def __repr__(self):
        return f'<StoreProfile {self.store_name}>'

    @classmethod
    def get_active_profile(cls):
        """Get the active store profile"""
        return cls.query.filter_by(is_active=True).first()

    @property
    def formatted_address(self):
        """Get formatted address for labels"""
        address_parts = [self.store_address]
        if self.store_city:
            address_parts.append(self.store_city)
        if self.store_postal_code:
            address_parts.append(self.store_postal_code)
        return ', '.join(address_parts)

    @property
    def created_at_wib(self):
        """Get created_at in WIB timezone"""
        if self.created_at:
            utc_dt = self.created_at.replace(tzinfo=pytz.UTC)
            return utc_dt.astimezone(WIB_TIMEZONE)
        return None

    @property
    def updated_at_wib(self):
        """Get updated_at in WIB timezone"""
        if self.updated_at:
            utc_dt = self.updated_at.replace(tzinfo=pytz.UTC)
            return utc_dt.astimezone(WIB_TIMEZONE)
        return None

    @property
    def full_contact_info(self):
        """Get full contact information"""
        contact_parts = []
        if self.store_phone:
            contact_parts.append(f"Telp: {self.store_phone}")
        if self.store_email:
            contact_parts.append(f"Email: {self.store_email}")
        if self.whatsapp_number:
            contact_parts.append(f"WA: {self.whatsapp_number}")
        return ' | '.join(contact_parts)

# Chat System Models
class ChatRoom(db.Model):
    __tablename__ = 'chat_rooms'

    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(100), unique=True, nullable=False)
    buyer_id = db.Column(Integer, nullable=True)  # Removed ForeignKey constraint to match Django
    buyer_name = db.Column(String(255), nullable=True)  # Increased length to match Django
    buyer_email = db.Column(String(254), nullable=True)  # Increased length to match Django
    is_active = db.Column(Boolean, default=True)
    created_at = db.Column(DateTime, default=get_utc_time)

    # Relationships
    messages = relationship('ChatMessage', backref='room', lazy=True, cascade='all, delete-orphan')
    sessions = relationship('ChatSession', backref='room', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<ChatRoom {self.name}>'

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'

    id = db.Column(Integer, primary_key=True)
    room_id = db.Column(Integer, ForeignKey('chat_rooms.id'), nullable=False)
    user_id = db.Column(Integer, ForeignKey('users.id'), nullable=False)
    user_name = db.Column(String(255), nullable=False)  # Increased length to match Django
    user_email = db.Column(String(254), nullable=True)  # Made nullable and increased length
    message = db.Column(Text, nullable=False)
    sender_type = db.Column(String(10), default='buyer')  # buyer, admin, staff
    product_id = db.Column(Integer, nullable=True)  # Removed ForeignKey constraint to match Django
    media_url = db.Column(String(500), nullable=True, default=None)  # Increased length to match Django
    media_type = db.Column(String(20), nullable=True, default=None)  # Increased length to match Django  
    media_filename = db.Column(String(255), nullable=True, default=None)  # Added default None
    is_read = db.Column(Boolean, default=False)
    is_deleted = db.Column(Boolean, default=False)
    created_at = db.Column(DateTime, default=get_utc_time)
    updated_at = db.Column(DateTime, default=get_utc_time, onupdate=get_utc_time)

    # Relationships
    sender = relationship('User', backref='chat_messages', lazy=True)
    # Note: tagged_product relationship removed to avoid foreign key constraint issues
    # Use models.Product.query.get(self.product_id) to get product when needed

    def __repr__(self):
        return f'<ChatMessage {self.user_name}: {self.message[:50]}...>'

    def to_dict(self):
        return {
            'id': self.id,
            'room_id': self.room_id,
            'user_id': self.user_id,
            'user_name': self.user_name,
            'user_email': self.user_email,
            'message': self.message,
            'sender_type': self.sender_type,
            'product_id': self.product_id,
            'media_url': self.media_url,
            'media_type': self.media_type,
            'media_filename': self.media_filename,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat(),
            'timestamp': self.created_at.strftime('%H:%M'),
            'product_info': None # Product info is no longer directly related. Fetch separately if needed.
        }

class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'

    id = db.Column(Integer, primary_key=True)
    room_id = db.Column(Integer, ForeignKey('chat_rooms.id'), nullable=False)
    user_id = db.Column(Integer, nullable=False)  # Removed ForeignKey constraint to match Django
    user_name = db.Column(String(255), nullable=False)  # Increased length to match Django
    user_email = db.Column(String(254), nullable=True)  # Made nullable and increased length
    user_role = db.Column(String(20), default='buyer')
    started_at = db.Column(DateTime, default=get_utc_time)
    ended_at = db.Column(DateTime, nullable=True)
    is_active = db.Column(Boolean, default=True)

    # Note: user relationship removed to avoid foreign key constraint issues
    # Use models.User.query.get(self.user_id) to get user when needed

    def __repr__(self):
        return f'<ChatSession {self.user_name} in {self.room.name}>'