
# Panduan Developer Hurtrock Music Store

## Daftar Isi
- [Arsitektur Sistem](#arsitektur-sistem)
- [Tech Stack](#tech-stack)
- [Setup Development Environment](#setup-development-environment)
- [Struktur Project](#struktur-project)
- [Database Schema](#database-schema)
- [API Documentation](#api-documentation)
- [Frontend Architecture](#frontend-architecture)
- [Backend Architecture](#backend-architecture)
- [Authentication & Authorization](#authentication--authorization)
- [Payment Integration](#payment-integration)
- [Real-time Chat System](#real-time-chat-system)
- [File Upload & Management](#file-upload--management)
- [Testing](#testing)
- [Deployment](#deployment)
- [Performance Optimization](#performance-optimization)
- [Security Guidelines](#security-guidelines)
- [Troubleshooting](#troubleshooting)

## Arsitektur Sistem

### System Overview

Hurtrock Music Store menggunakan arsitektur **MVC (Model-View-Controller)** dengan **Flask** sebagai framework utama. Aplikasi dirancang dengan pendekatan **monolithic** yang modular dan dapat di-scale horizontal.

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (Templates)   │◄──►│   (Flask App)   │◄──►│   (PostgreSQL)  │
│   Bootstrap 5   │    │   SQLAlchemy    │    │   Relational    │
│   JavaScript    │    │   Socket.IO     │    │   ACID          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CDN/Static    │    │   Payment       │    │   File Storage  │
│   Images        │    │   Gateway       │    │   Local/Cloud   │
│   CSS/JS        │    │   Stripe/MT     │    │   Images        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Component Architecture

- **Presentation Layer**: Jinja2 Templates + Bootstrap 5 + Vanilla JS
- **Business Logic Layer**: Flask Routes + Service Classes
- **Data Access Layer**: SQLAlchemy ORM + PostgreSQL
- **Integration Layer**: Payment Gateways + Email Services
- **Real-time Layer**: Socket.IO untuk chat dan notifications

## Tech Stack

### Backend
- **Python 3.11+**: Programming language utama
- **Flask 3.1.2**: Web framework
- **SQLAlchemy 2.0+**: ORM dan database abstraction
- **PostgreSQL**: Primary database
- **Flask-Login**: User session management
- **Flask-WTF**: Form handling dan CSRF protection
- **Flask-Migrate**: Database migration
- **Flask-SocketIO**: Real-time communication

### Frontend
- **Jinja2**: Template engine
- **Bootstrap 5.3**: CSS framework
- **Vanilla JavaScript**: Client-side logic
- **Font Awesome**: Icon library
- **Google Fonts**: Typography

### Payment & Integration
- **Stripe**: International payment gateway
- **Midtrans**: Indonesian payment gateway
- **Socket.IO**: Real-time messaging

### Development Tools
- **Git**: Version control
- **pip/uv**: Package management
- **Python-dotenv**: Environment variables
- **Werkzeug**: WSGI utilities

## Setup Development Environment

### Prerequisites

```bash
# Python 3.11+
python --version

# PostgreSQL
psql --version

# Git
git --version
```

### Installation Steps

1. **Clone Repository**:
```bash
git clone [repository-url]
cd hurtrock-music-store
```

2. **Auto Installation (Recommended)**:
```bash
# Universal installation
chmod +x install.sh
./install.sh

# Atau untuk Linux server
chmod +x install-linux.sh
./install-linux.sh
```

3. **Manual Installation**:
```bash
# Install Dependencies
pip install -r requirements.txt

# Environment Variables
cp .env.example .env
# Edit .env dengan konfigurasi yang sesuai

# Database Setup
python migrate_db.py

# Load sample data
python sample_data.py
```

4. **Run Application**:

**Using Unified Server (Recommended)**:
```bash
python server.py
```

**Using Start Script**:
```bash
./start_server.sh
```

**Development Mode (Flask only)**:
```bash
python main.py
```

### Unified Server Architecture

Server.py menjalankan Flask dan Django secara bersamaan:
- **Flask Main App**: Port 5000
- **Django Chat Service**: Port 8000
- **Automatic Setup**: Database migration dan service coordination
- **Package Ready**: Siap untuk PyInstaller packaging

### Environment Variables

```bash
# .env file
SESSION_SECRET=your-secret-key-here
DATABASE_URL=postgresql://user:password@localhost/hurtrock_music_store
STRIPE_SECRET_KEY=sk_test_your_stripe_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_key
MIDTRANS_SERVER_KEY=your_midtrans_server_key
MIDTRANS_CLIENT_KEY=your_midtrans_client_key
FLASK_ENV=development
FLASK_DEBUG=1
```

## Struktur Project

```
hurtrock-music-store/
├── main.py                 # Entry point aplikasi
├── database.py             # Database configuration
├── models.py               # SQLAlchemy models
├── requirements.txt        # Python dependencies
├── pyproject.toml         # Project metadata
├── sample_data.py         # Sample data generator
├── migrate_db.py          # Database migration script
├── migrations/            # Database migrations
│   ├── alembic.ini
│   ├── env.py
│   └── versions/
├── static/                # Static assets
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── script.js
│   └── images/
├── templates/             # Jinja2 templates
│   ├── base.html          # Base template
│   ├── index.html         # Homepage
│   ├── admin/             # Admin templates
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── products.html
│   │   ├── chat_detail.html
│   │   └── ...
│   └── ...
├── dokumentasi/           # Documentation
│   ├── USER_GUIDE.md
│   ├── ADMIN_GUIDE.md
│   ├── DEVELOPER_GUIDE.md
│   └── MAINTAINER_GUIDE.md
└── README.md              # Project overview
```

## Database Schema

### Entity Relationship Diagram (ERD)

```mermaid
erDiagram
    User ||--o{ Order : creates
    User ||--o{ CartItem : has
    User ||--o{ ChatRoom : initiates
    
    Order ||--o{ OrderItem : contains
    Product ||--o{ OrderItem : ordered_in
    Product ||--o{ CartItem : added_to
    Product }o--|| Category : belongs_to
    Product }o--o| Supplier : supplied_by
    
    ChatRoom ||--o{ ChatMessage : contains
    ChatMessage }o--o| Product : tags
    
    Order }o--o| ShippingService : ships_via
    
    PaymentConfiguration ||--o{ Order : processes
```

### Core Models

```python
# User Model
class User(UserMixin, db.Model):
    id = db.Column(Integer, primary_key=True)
    email = db.Column(String(120), unique=True, nullable=False)
    password_hash = db.Column(String(255), nullable=False)
    name = db.Column(String(100), nullable=False)
    phone = db.Column(String(20))
    address = db.Column(Text)
    role = db.Column(String(20), default='buyer')  # admin, staff, buyer
    active = db.Column(Boolean, default=True)
    created_at = db.Column(DateTime, default=datetime.utcnow)

# Product Model
class Product(db.Model):
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(200), nullable=False)
    description = db.Column(Text)
    price = db.Column(Numeric(10, 2), nullable=False)
    stock_quantity = db.Column(Integer, default=0)
    image_url = db.Column(String(255))
    brand = db.Column(String(100))
    model = db.Column(String(100))
    category_id = db.Column(Integer, ForeignKey('categories.id'))
    supplier_id = db.Column(Integer, ForeignKey('suppliers.id'))
    weight = db.Column(Numeric(8, 2), default=0)  # dalam gram
    length = db.Column(Numeric(8, 2), default=0)  # dalam cm
    width = db.Column(Numeric(8, 2), default=0)
    height = db.Column(Numeric(8, 2), default=0)
    is_active = db.Column(Boolean, default=True)
    is_featured = db.Column(Boolean, default=False)
    created_at = db.Column(DateTime, default=datetime.utcnow)

# Order Model
class Order(db.Model):
    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer, ForeignKey('users.id'))
    total_amount = db.Column(Numeric(10, 2), nullable=False)
    status = db.Column(String(50), default='pending')
    shipping_service_id = db.Column(Integer, ForeignKey('shipping_services.id'))
    shipping_cost = db.Column(Numeric(10, 2), default=0)
    shipping_address = db.Column(Text)
    tracking_number = db.Column(String(100))
    created_at = db.Column(DateTime, default=datetime.utcnow)
```

### Migration Commands

```bash
# Inisialisasi migration (hanya sekali)
flask db init

# Buat migration baru setelah perubahan model
flask db migrate -m "Description of changes"

# Apply migration ke database
flask db upgrade

# Rollback migration
flask db downgrade

# Lihat history migration
flask db history
```

## API Documentation

### Authentication Required Endpoints

Semua endpoint yang memerlukan authentication menggunakan `@login_required` decorator.

### Chat API

**GET /api/chat/messages**
- **Description**: Mengambil semua pesan chat user
- **Authentication**: Required
- **Response**:
```json
{
  "success": true,
  "messages": [
    {
      "id": 1,
      "message": "Hello",
      "sender_type": "user",
      "timestamp": "14:30",
      "product_id": null
    }
  ]
}
```

**POST /api/chat/send**
- **Description**: Mengirim pesan chat
- **Authentication**: Required
- **Body**:
```json
{
  "message": "Product inquiry",
  "product_id": 123
}
```
- **Response**:
```json
{
  "success": true,
  "message_id": 456
}
```

**POST /api/chat/clear**
- **Description**: Menghapus semua pesan chat user
- **Authentication**: Required
- **Response**:
```json
{
  "success": true
}
```

### Search API

**GET /search**
- **Description**: Mencari produk
- **Parameters**: 
  - `q`: Query string (min 2 characters)
- **Response**:
```json
[
  {
    "id": 1,
    "name": "Yamaha F310",
    "price": "1500000",
    "image_url": "/static/images/guitar.jpg",
    "brand": "Yamaha",
    "description": "Gitar akustik untuk pemula..."
  }
]
```

### Admin API

**POST /admin/send_reply**
- **Description**: Admin mengirim balasan chat
- **Authentication**: Required (Staff/Admin)
- **Body**:
```form-data
room_id=123
message=Terima kasih pertanyaannya
product_id=456
csrf_token=xxx
```

**GET /api/chat/pending_count**
- **Description**: Jumlah chat pending untuk admin
- **Authentication**: Required (Staff/Admin)
- **Response**:
```json
{
  "count": 5
}
```

## Frontend Architecture

### Template Structure

**Base Template** (`templates/base.html`):
- Header dengan navigation
- Search functionality
- Footer
- JavaScript dan CSS includes
- Flash message handling

**Page Templates**:
- Extend dari base template
- Block untuk content spesifik
- Page-specific JavaScript dan CSS

### JavaScript Architecture

**Script Organization**:
```javascript
// Global variables dan konfigurasi
const CONFIG = {
    SEARCH_DELAY: 300,
    CHAT_POLL_INTERVAL: 5000
};

// Search functionality
function initializeSearch() {
    // Search implementation
}

// Chat functionality
function initializeChat() {
    // Chat implementation
}

// Product functionality
function initializeProducts() {
    // Product implementation
}

// Document ready initialization
document.addEventListener('DOMContentLoaded', function() {
    initializeSearch();
    initializeChat();
    initializeProducts();
});
```

### Responsive Design

**Breakpoints**:
```css
/* Mobile First Approach */
/* Base styles untuk mobile */

@media (min-width: 576px) {
    /* Small tablets */
}

@media (min-width: 768px) {
    /* Tablets */
}

@media (min-width: 992px) {
    /* Desktop */
}

@media (min-width: 1200px) {
    /* Large desktop */
}
```

### CSS Architecture

**Style Organization**:
```css
/* 1. CSS Variables */
:root {
    --orange-primary: #ff7b00;
    --black-primary: #1a1a1a;
    --transition-smooth: all 0.3s ease;
}

/* 2. Base Styles */
body { ... }

/* 3. Layout Components */
.navbar { ... }
.footer { ... }

/* 4. UI Components */
.btn-orange { ... }
.card-product { ... }

/* 5. Page Specific */
.admin-sidebar { ... }
.chat-widget { ... }

/* 6. Utilities */
.text-orange { ... }
.bg-glass { ... }
```

## Backend Architecture

### Application Factory Pattern

```python
# main.py
def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    socketio.init_app(app)
    
    # Register blueprints
    from routes import main_bp, admin_bp, api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app
```

### Route Organization

**Main Routes** (customer-facing):
```python
@app.route('/')
def index():
    # Homepage dengan featured products
    
@app.route('/products')
def products():
    # Product catalog dengan filtering
    
@app.route('/product/<int:product_id>')
def product_detail(product_id):
    # Detail produk
```

**Admin Routes** (admin panel):
```python
@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    # Admin dashboard
    
@app.route('/admin/products')
@login_required
@staff_required
def admin_products():
    # Product management
```

**API Routes** (AJAX endpoints):
```python
@app.route('/api/chat/send', methods=['POST'])
@login_required
@csrf.exempt
def api_chat_send():
    # Chat API endpoint
```

### Service Layer Pattern

```python
# services/product_service.py
class ProductService:
    @staticmethod
    def get_featured_products(limit=8):
        return Product.query.filter_by(
            is_active=True, 
            is_featured=True
        ).limit(limit).all()
    
    @staticmethod
    def search_products(query, category_id=None):
        # Product search logic
        
    @staticmethod
    def update_stock(product_id, quantity_change):
        # Stock management logic
```

### Decorators

**Custom Decorators**:
```python
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Access denied. Admin required.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def staff_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or (not current_user.is_admin and not current_user.is_staff):
            flash('Access denied. Staff or admin required.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function
```

## Authentication & Authorization

### User Roles

1. **Admin**: Full access ke semua fitur
2. **Staff**: Access ke product management dan customer service
3. **Buyer**: Regular customer access

### Session Management

```python
# Flask-Login configuration
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = 'Silakan login untuk mengakses halaman ini.'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
```

### Password Security

```python
from werkzeug.security import generate_password_hash, check_password_hash

# Hash password saat register
hashed_password = generate_password_hash(password)

# Verify password saat login
if user and check_password_hash(user.password_hash, password):
    login_user(user)
```

### CSRF Protection

```python
# Inisialisasi CSRF
csrf = CSRFProtect(app)

# Exempt API endpoints
@app.route('/api/chat/send', methods=['POST'])
@csrf.exempt
def api_chat_send():
    # API logic
```

## Payment Integration

### Stripe Integration

**Configuration**:
```python
stripe.api_key = payment_config.stripe_secret_key

# Create checkout session
checkout_session = stripe.checkout.Session.create(
    line_items=line_items,
    mode='payment',
    success_url=f'https://{domain}/payment-success',
    cancel_url=f'https://{domain}/cart',
    customer_email=current_user.email,
)
```

### Midtrans Integration

**Configuration**:
```python
snap = midtransclient.Snap(
    is_production=not payment_config.is_sandbox,
    server_key=payment_config.midtrans_server_key,
    client_key=payment_config.midtrans_client_key
)

# Create transaction
transaction = snap.create_transaction(param)
```

### Payment Flow

1. **User** selects products dan checkout
2. **System** calculates total dengan shipping
3. **Payment Gateway** processes payment
4. **Webhook** updates order status
5. **Email** notification dikirim ke user
6. **Admin** dapat process order untuk shipping

## Real-time Chat System

### Socket.IO Implementation

**Server-side**:
```python
from flask_socketio import SocketIO, emit, join_room, leave_room

socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('join')
def on_join(data):
    if current_user.is_authenticated:
        if current_user.is_admin or current_user.is_staff:
            join_room('admin_room')
        else:
            join_room(f'user_{current_user.id}')

@socketio.on('disconnect')
def on_disconnect():
    # Handle disconnect
```

**Client-side**:
```javascript
const socket = io();

socket.emit('join', {});

socket.on('new_message', function(data) {
    displayMessage(data.message, data.sender_type);
});
```

### Chat Features

1. **Real-time messaging** antara user dan admin
2. **Product tagging** dalam chat
3. **Unread message badges**
4. **Message history** tersimpan di database
5. **Admin notifications** untuk chat baru

## File Upload & Management

### Image Upload

```python
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def compress_image(image_path, max_size_mb=1):
    img = Image.open(image_path)
    
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGB')
    
    quality = 85
    while True:
        img.save(image_path, 'JPEG', quality=quality, optimize=True)
        file_size_mb = os.path.getsize(image_path) / (1024 * 1024)
        
        if file_size_mb <= max_size_mb or quality <= 20:
            break
        quality -= 10
    
    return image_path
```

### File Organization

```
static/
├── images/
│   ├── products/          # Product images
│   ├── categories/        # Category images
│   ├── uploads/           # User uploads
│   └── placeholders/      # Placeholder images
├── css/
│   └── style.css
└── js/
    └── script.js
```

## Testing

### Unit Testing

```python
import unittest
from main import create_app
from database import db
from models import User, Product

class ProductTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with self.app.app_context():
            db.create_all()
    
    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_product_creation(self):
        with self.app.app_context():
            product = Product(
                name='Test Guitar',
                price=1000000,
                category_id=1
            )
            db.session.add(product)
            db.session.commit()
            
            self.assertEqual(product.name, 'Test Guitar')
            self.assertEqual(product.price, 1000000)
```

### Integration Testing

```python
def test_checkout_flow(self):
    with self.client as c:
        # Login
        c.post('/login', data={'email': 'test@test.com', 'password': 'password'})
        
        # Add to cart
        c.post('/add_to_cart/1', data={'quantity': 1})
        
        # Checkout
        response = c.post('/checkout', data={
            'shipping_service_id': 1,
            'payment_config_id': 1
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect to payment
```

### Testing Commands

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_products.py

# Run with coverage
python -m pytest --cov=main

# Run with verbose output
python -m pytest -v
```

## Deployment

### Environment Configuration

**Production Settings**:
```python
# Production environment
FLASK_ENV=production
FLASK_DEBUG=0
DATABASE_URL=postgresql://user:pass@host:5432/db
SESSION_SECRET=very-secure-secret-key
STRIPE_SECRET_KEY=sk_live_...
MIDTRANS_SERVER_KEY=production_key
```

### Database Migration

```bash
# Production deployment
flask db upgrade

# Rollback jika ada masalah
flask db downgrade
```

### Static File Handling

**Development**:
```python
app.run(debug=True)  # Flask serves static files
```

**Production**:
```nginx
# Nginx configuration
location /static {
    alias /path/to/app/static;
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### Process Management

**Systemd Service**:
```ini
[Unit]
Description=Hurtrock Music Store
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/hurtrock
Environment=PATH=/var/www/hurtrock/venv/bin
ExecStart=/var/www/hurtrock/venv/bin/gunicorn --workers 3 --bind unix:hurtrock.sock -m 007 main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

## Performance Optimization

### Database Optimization

**Query Optimization**:
```python
# Eager loading untuk menghindari N+1 queries
products = Product.query.options(
    joinedload(Product.category),
    joinedload(Product.supplier)
).filter_by(is_active=True).all()

# Index pada kolom yang sering di-query
class Product(db.Model):
    name = db.Column(String(200), nullable=False, index=True)
    category_id = db.Column(Integer, ForeignKey('categories.id'), index=True)
```

**Pagination**:
```python
products = Product.query.paginate(
    page=page, 
    per_page=20, 
    error_out=False
)
```

### Caching Strategy

```python
from flask_caching import Cache

cache = Cache(app)

@cache.cached(timeout=300)  # Cache 5 menit
def get_featured_products():
    return Product.query.filter_by(is_featured=True).all()
```

### Frontend Optimization

**Image Optimization**:
- Kompres gambar sebelum upload
- Lazy loading untuk gambar
- WebP format support
- Responsive images

**JavaScript Optimization**:
- Minify JS dan CSS
- Bundle dan compress assets
- Defer non-critical JavaScript
- Use CDN untuk libraries

## Security Guidelines

### Input Validation

```python
from wtforms import ValidationError

def validate_email(form, field):
    user = User.query.filter_by(email=field.data).first()
    if user:
        raise ValidationError('Email already registered.')
```

### SQL Injection Prevention

```python
# Menggunakan SQLAlchemy ORM (aman)
users = User.query.filter_by(email=email).all()

# Jika harus raw SQL, gunakan parameterized queries
result = db.session.execute(
    text("SELECT * FROM users WHERE email = :email"), 
    {"email": email}
)
```

### XSS Prevention

```html
<!-- Jinja2 auto-escape HTML -->
<p>{{ user.name }}</p>  <!-- Aman -->

<!-- Jika perlu HTML, gunakan |safe dengan hati-hati -->
<p>{{ user.bio|safe }}</p>  <!-- Pastikan data sudah di-sanitize -->
```

### CSRF Protection

```html
<!-- Include CSRF token dalam form -->
<form method="POST">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
    <!-- form fields -->
</form>
```

### Secure Headers

```python
@app.after_request
def set_secure_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
```

## Packaging untuk Distribusi

### PyInstaller Setup

Aplikasi telah didesain untuk packaging:

```bash
# Install PyInstaller
pip install pyinstaller

# Basic executable
pyinstaller --onefile server.py

# Dengan assets
pyinstaller --onefile \
  --add-data "templates:templates" \
  --add-data "static:static" \
  --add-data "chat_service:chat_service" \
  server.py

# GUI application (tanpa console)
pyinstaller --onefile --windowed \
  --add-data "templates:templates" \
  --add-data "static:static" \
  --add-data "chat_service:chat_service" \
  server.py
```

### Distribusi

**Windows Executable**:
- Hasil: `dist/server.exe`
- Standalone, tidak perlu Python install
- Include semua dependencies

**Linux Package (.deb)**:
```bash
# Install fpm
gem install fpm

# Create package
fpm -s dir -t deb \
  -n hurtrock-music-store \
  -v 1.0.0 \
  --description "Hurtrock Music Store" \
  dist/server=/usr/local/bin/
```

**macOS Application**:
```bash
# Create .app bundle
pyinstaller --onefile --windowed \
  --name "Hurtrock Music Store" \
  server.py
```

### Docker Alternative

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 5000 8000
CMD ["python", "server.py"]
```

## Troubleshooting

### Common Issues

**Database Connection Error**:
```bash
# Check database status
pg_isready -h localhost -p 5432

# Check connection string
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1;"
```

**Migration Issues**:
```bash
# Reset migration (development only)
rm -rf migrations/
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Fix migration conflicts
flask db merge heads
```

**Import Errors**:
```python
# Check Python path
import sys
print(sys.path)

# Check installed packages
pip list | grep flask
```

**Socket.IO Connection Issues**:
```javascript
// Debug Socket.IO connection
socket.on('connect', function() {
    console.log('Connected to server');
});

socket.on('disconnect', function() {
    console.log('Disconnected from server');
});

socket.on('connect_error', function(error) {
    console.log('Connection error:', error);
});
```

### Debugging Tools

**Flask Debug Mode**:
```python
app.run(debug=True)  # Development only
```

**Logging**:
```python
import logging

logging.basicConfig(level=logging.DEBUG)
app.logger.debug('Debug message')
app.logger.info('Info message')
app.logger.error('Error message')
```

**Database Debugging**:
```python
# SQLAlchemy query debugging
app.config['SQLALCHEMY_ECHO'] = True
```

### Performance Monitoring

**Query Profiling**:
```python
from flask_debugtoolbar import DebugToolbarExtension

app.config['DEBUG_TB_ENABLED'] = True
toolbar = DebugToolbarExtension(app)
```

**Application Monitoring**:
```python
import time

@app.before_request
def before_request():
    g.start_time = time.time()

@app.after_request
def after_request(response):
    duration = time.time() - g.start_time
    app.logger.info(f'Request took {duration:.2f}s')
    return response
```

---

## Development Workflow

### Git Workflow

```bash
# Feature development
git checkout -b feature/new-feature
git add .
git commit -m "Add new feature"
git push origin feature/new-feature

# Create pull request
# Code review
# Merge to main
```

### Code Style

**Python (PEP 8)**:
```python
# Use 4 spaces for indentation
# Max line length: 88 characters
# Use snake_case for variables dan functions
# Use PascalCase untuk classes
```

**JavaScript**:
```javascript
// Use 2 spaces for indentation
// Use camelCase untuk variables dan functions
// Use semicolons
// Use const/let instead of var
```

### Documentation

- **Code Comments**: Explain complex logic
- **Docstrings**: Untuk functions dan classes
- **API Documentation**: Keep updated
- **README**: Setup instructions

---

*Panduan ini akan terus diperbarui seiring dengan pengembangan aplikasi. Untuk pertanyaan teknis lebih lanjut, silakan hubungi tim development.*
