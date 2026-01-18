"""
Django settings for backend_site project.
"""

from pathlib import Path
import os
import dj_database_url


# Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR points to your 'backend' folder
BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent   # 👈 this points to project-root
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = "/"
# SECURITY WARNING: keep the secret key used in production secret!
#SECRET_KEY = 'django-insecure-swagat-caterers-dev-key-123'
SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-swagat-caterers-dev-key-123"
)

# SECURITY WARNING: don't run with debug turned on in production!
#DEBUG = True
DEBUG = os.environ.get("DEBUG", "True") == "True"

# ALLOWED_HOSTS = []
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "swagat-caterers-platform-production.up.railway.app"
]
# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'djoser',
    'corsheaders',
    'catering.apps.CateringConfig',
    'cloudinary_storage',
    'cloudinary',
    'anymail',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend_site.urls'

# --- TEMPLATE CONFIGURATION (CORRECTED) ---
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # <--- Templates go here
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

WSGI_APPLICATION = 'backend_site.wsgi.application'

# Database

DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL)
    }
    # Important: Railway Postgres requires SSL in production
    DATABASES['default']['CONN_MAX_AGE'] = 600
    # Use this to avoid SSL errors on some Railway plans
    DATABASES['default']['OPTIONS'] = {'sslmode': 'require'}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'catering_db',
            'USER': 'makadiyapreet',
            'PASSWORD': '',
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }
# DATABASES = {
#  'default': {
#        'ENGINE': 'django.db.backends.postgresql',
#        'NAME': 'catering_db',
#        'USER': 'makadiyapreet',
#        'PASSWORD': '',
#        'HOST': 'localhost',
#        'PORT': '5432',
#    }
#} 

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# --- STATIC FILES (CORRECTED) ---
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'


# FIX: Look in the sibling 'static' folder for static assets too
STATICFILES_DIRS = [
    BASE_DIR / 'templates',
]

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS
CORS_ALLOW_ALL_ORIGINS = True

# Rest Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication', # Added for decorator
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.BasicAuthentication',),
}

# --- EMAIL SETTINGS (SMTP) ---
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_BACKEND = 'anymail.backends.sendinblue.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST = 'smtp-relay.brevo.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'swagatcaterersofficial@gmail.com'
# EMAIL_HOST_PASSWORD = 'cqib xpwa cxwo mtri'  # App Password
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = 'swagatcaterersofficial@gmail.com'
EMAIL_TIMEOUT = 10

# Custom User & Auth
AUTH_USER_MODEL = 'catering.User'
AUTHENTICATION_BACKENDS = [
    'catering.backends.EmailPhoneUsernameBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Djoser
DJOSER = {
    'SEND_ACTIVATION_EMAIL': False, # Turn this OFF
    'USER_CREATE_PASSWORD_RETYPE': True,
    'SERIALIZERS': {
        'user_create': 'catering.serializers.UserCreateSerializer',
    },
}


# Media Files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

CSRF_TRUSTED_ORIGINS = [
    'https://swagat-caterers-platform-production.up.railway.app',
    # "https://swagatcaterers.in", # If you have a custom domain
]

CORS_ALLOWED_ORIGINS = [
    'https://swagat-caterers-platform-production.up.railway.app'
]

if not DEBUG:
    # Tell Django it's behind a secure proxy (Railway)
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    # Force all connections to HTTPS
    SECURE_SSL_REDIRECT = True
    
    # Ensure cookies are only sent over HTTPS
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # Recommended for performance on Railway
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Cloudinary Config (Get these from your Cloudinary Dashboard)
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET')
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

ANYMAIL = {
    "SENDINBLUE_API_KEY": os.environ.get('SENDINBLUE_API_KEY'),
    }