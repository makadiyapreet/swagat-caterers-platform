"""
Django settings for backend_site project.
Production-hardened configuration.
"""

from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')
PROJECT_ROOT = BASE_DIR.parent

# Auth redirects
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = "/"

# ========================
# SECURITY
# ========================

# SECRET_KEY: Must be set via environment variable. Crashes if missing in production.
SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError(
        "SECRET_KEY environment variable is not set. "
        "Generate one with: python -c \"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())\""
    )

# DEBUG: Defaults to False for safety. Must explicitly set DEBUG=True in .env for development.
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.environ.get(
    'ALLOWED_HOSTS',
    '127.0.0.1,localhost,swagatcaterers.in,www.swagatcaterers.in,swagat-caterers-platform-production.up.railway.app'
).split(',')

# ========================
# APPLICATION DEFINITION
# ========================

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
    'blog.apps.BlogConfig',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend_site.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'catering.context_processors.user_permissions',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend_site.wsgi.application'

# ========================
# DATABASE
# ========================

DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL)
    }
    DATABASES['default']['CONN_MAX_AGE'] = 600
    DATABASES['default']['OPTIONS'] = {'sslmode': 'require'}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'catering_db',
            'USER': os.environ.get('DB_USER', 'makadiyapreet'),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }

# ========================
# PASSWORD VALIDATION
# ========================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
    {'NAME': 'catering.validators.ZxcvbnPasswordValidator', 'OPTIONS': {'min_score': 2}},
]

# ========================
# INTERNATIONALIZATION
# ========================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# ========================
# STATIC FILES
# ========================

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ========================
# CORS
# ========================

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    'https://swagatcaterers.in',
    'https://www.swagatcaterers.in',
    'https://swagat-caterers-platform-production.up.railway.app',
]

# ========================
# REST FRAMEWORK
# ========================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
}

# ========================
# EMAIL (Brevo / Sendinblue)
# ========================

EMAIL_BACKEND = 'anymail.backends.sendinblue.EmailBackend'
EMAIL_HOST = 'smtp-relay.brevo.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'swagatcaterersofficial@gmail.com'
EMAIL_HOST_PASSWORD = os.environ.get('BREVO_SMTP_KEY')
DEFAULT_FROM_EMAIL = 'swagatcaterersofficial@gmail.com'
EMAIL_TIMEOUT = 10
ADMIN_EMAIL = 'swagatcaterersofficial@gmail.com'

ANYMAIL = {
    "SENDINBLUE_API_KEY": os.environ.get('BREVO_SMTP_KEY'),
}

# ========================
# AUTHENTICATION
# ========================

AUTH_USER_MODEL = 'catering.User'
AUTHENTICATION_BACKENDS = [
    'catering.backends.EmailPhoneUsernameBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# ========================
# DJOSER
# ========================

DJOSER = {
    'LOGIN_FIELD': 'email',
    'USER_CREATE_PASSWORD_RETYPE': True,
    'USERNAME_CHANGED_EMAIL_CONFIRMATION': True,
    'PASSWORD_CHANGED_EMAIL_CONFIRMATION': True,
    'SEND_CONFIRMATION_EMAIL': False,
    'SET_USERNAME_RETYPE': True,
    'SET_PASSWORD_RETYPE': True,
    'PASSWORD_RESET_CONFIRM_URL': 'password/reset/confirm/{uid}/{token}',
    'USERNAME_RESET_CONFIRM_URL': 'email/reset/confirm/{uid}/{token}',
    'ACTIVATION_URL': 'activate/{uid}/{token}',
    'SEND_ACTIVATION_EMAIL': False,
    'SERIALIZERS': {
        'user_create': 'catering.serializers.UserCreateSerializer',
        'user_create_password_retype': 'catering.serializers.UserCreateSerializer',
        'user': 'catering.serializers.UserSerializer',
        'current_user': 'catering.serializers.UserSerializer',
        'user_delete': 'djoser.serializers.UserDeleteSerializer',
    },
}

# ========================
# MEDIA FILES (Cloudinary in production)
# ========================

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# ========================
# CSRF TRUSTED ORIGINS
# ========================

CSRF_TRUSTED_ORIGINS = [
    'https://swagatcaterers.in',
    'https://www.swagatcaterers.in',
    'https://swagat-caterers-platform-production.up.railway.app',
]

# ========================
# SECURITY HARDENING
# ========================

# Always set these
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Production-only HTTPS enforcement
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_HTTPONLY = False  # Must be False so JavaScript can read csrftoken cookie
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
else:
    # Development: no HTTPS enforcement
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    CSRF_COOKIE_HTTPONLY = False  # Must be False so JavaScript can read csrftoken cookie

# ========================
# THIRD-PARTY API KEYS
# ========================

GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
OPENWEATHERMAP_API_KEY = os.environ.get('OPENWEATHERMAP_API_KEY', '')
BREVO_SMTP_KEY = os.environ.get('BREVO_SMTP_KEY', '')
ADMIN_ALERT_EMAIL = os.environ.get('ADMIN_ALERT_EMAIL', 'swagatcaterersofficial@gmail.com')