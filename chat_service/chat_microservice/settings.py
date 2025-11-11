"""
Django settings for chat_microservice project.
"""

from pathlib import Path
import os
import socket

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-dev-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG', 'False').lower() == 'true'

# Get current domains from environment first
DOMAINS = os.environ.get('DOMAINS', '')

# Build allowed hosts list dynamically but securely
def build_allowed_hosts():
    hosts = ['localhost', '127.0.0.1', '0.0.0.0']

    # Add replit.dev domains with more patterns
    repl_slug = os.environ.get('REPL_SLUG', '')
    repl_owner = os.environ.get('REPL_OWNER', '')

    # Try to get current Replit host from various sources
    if repl_slug and repl_owner:
        hosts.extend([
            f"{repl_slug}.{repl_owner}.repl.co",
            f"{repl_slug}--{repl_owner}.repl.co",
        ])

    # Add pattern for current Replit workspace
    try:
        hostname = socket.getfqdn()
        if 'replit.dev' in hostname or 'repl.co' in hostname:
            hosts.append(hostname)
    except:
        pass

    # Add all Replit workspace patterns (including pike and sisko patterns)
    hosts.extend([
        '*.replit.dev',
        '*.repl.co',
        '*.pike.replit.dev',
        '*.sisko.replit.dev',
        # Add specific patterns from Replit deployment
        '2c314e81-d857-47a4-8b90-1cfa416fd21e-00-3a775t0rpzl4u.pike.replit.dev',
        '70785d3e-15df-4763-8573-a050f2824067-00-bic1miq7o55e.sisko.replit.dev',
    ])

    # Add custom domains if available
    if DOMAINS:
        domains = DOMAINS.split(',')
        for domain in domains:
            domain = domain.strip()
            if domain:
                hosts.append(domain)

    # Add Cloudflare tunnel domains and IP addresses
    hosts.extend([
        'hurtrock-store.com',
        'www.hurtrock-store.com', 
        'chat.hurtrock-store.com',
        '*.hurtrock-store.com',
        # Allow IP addresses for direct access
        '172.31.82.130',  # Current container IP
        '*.172.31.82.130',
    ])

    # In development, allow all hosts for maximum compatibility
    if DEBUG:
        hosts.append('*')

    return list(dict.fromkeys(hosts))  # Remove duplicates

ALLOWED_HOSTS = build_allowed_hosts()

# Application definition
INSTALLED_APPS = [
    'daphne',  # ASGI server for Channels - must be first
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',
    'corsheaders',
    'rest_framework',
    'chat',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'chat_microservice.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'chat_microservice.wsgi.application'
ASGI_APPLICATION = 'chat_microservice.asgi.application'

# Database - Use PostgreSQL from environment (same as Flask)
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # Parse DATABASE_URL
    try:
        import dj_database_url
        DATABASES = {
            'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
        }
        # Add PostgreSQL-specific options only for PostgreSQL
        if 'postgresql' in DATABASE_URL or 'postgres' in DATABASE_URL:
            DATABASES['default']['OPTIONS'] = {
                'connect_timeout': 10,
                'sslmode': 'prefer',
            }
        # Enable atomic requests
        DATABASES['default']['ATOMIC_REQUESTS'] = True
    except ImportError:
        # Fallback manual parsing if dj_database_url not available
        import urllib.parse as urlparse
        url = urlparse.urlparse(DATABASE_URL)
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': url.path[1:] if url.path else 'postgres',
                'USER': url.username or 'postgres',
                'PASSWORD': url.password or '',
                'HOST': url.hostname or 'localhost',
                'PORT': url.port or 5432,
                'CONN_MAX_AGE': 600,
                'ATOMIC_REQUESTS': True,
                'OPTIONS': {
                    'connect_timeout': 10,
                    'sslmode': 'prefer',
                },
            }
        }
else:
    # SQLite fallback for development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
            'ATOMIC_REQUESTS': True,
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'id-id'
TIME_ZONE = 'Asia/Jakarta'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Channels Configuration
REDIS_URL = os.environ.get('REDIS_URL', None)

if REDIS_URL:
    # Production: Use Redis
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                'hosts': [REDIS_URL],
            },
        },
    }
else:
    # Development fallback: In-memory
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        },
    }

# CORS Configuration - Dynamic domain support with security
def build_cors_origins():
    origins = [
        "http://localhost:5000",
        "http://127.0.0.1:5000",
        "http://0.0.0.0:5000",
    ]

    # Add replit.dev domains
    replit_host = os.environ.get('REPL_ID', '')
    if replit_host:
        origins.extend([
            f"https://{replit_host}.replit.dev",
            f"http://{replit_host}.replit.dev",
            f"https://{replit_host}.repl.co",
            f"http://{replit_host}.repl.co",
        ])

    # Add current custom domains dynamically
    if DOMAINS:
        domains = DOMAINS.split(',')
        for domain in domains:
            domain = domain.strip()
            if domain:
                origins.extend([
                    f"https://{domain}",
                    f"http://{domain}",
                ])

    # Add Cloudflare tunnel domains (sesuai konfigurasi tunnel)
    origins.extend([
        "https://www.hurtrock-store.com",
        "http://www.hurtrock-store.com",
        "https://hurtrock-store.com",
        "http://hurtrock-store.com",
    ])

    return origins

# Use permissive CORS only in development for local area network access
# Allow all origins for maximum compatibility with tunnel and local area network
CORS_ALLOW_ALL_ORIGINS = True  # Allow all for tunnel and LAN compatibility
CORS_ALLOW_CREDENTIALS = False  # Using JWT only, no cookies needed
CORS_ALLOWED_ORIGINS = build_cors_origins()

# Set CSRF trusted origins for production security
CSRF_TRUSTED_ORIGINS = build_cors_origins() if not DEBUG else []

# JWT Configuration
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or os.environ.get('SESSION_SECRET') or SECRET_KEY
JWT_ALGORITHM = 'HS256'
JWT_ACCESS_TOKEN_LIFETIME = 86400

# Debug JWT configuration
if not JWT_SECRET_KEY:
    print("[WARNING] JWT_SECRET_KEY not configured properly")
else:
    print(f"[OK] JWT configured with secret key: {JWT_SECRET_KEY[:10]}...")

# Django REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'chat.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'channels': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}