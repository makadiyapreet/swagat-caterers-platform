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
DEBUG = os.getenv("DEBUG") == "True"

# ALLOWED_HOSTS = []
ALLOWED_HOSTS = os.environ.get(
    "ALLOWED_HOSTS",
    "127.0.0.1,localhost"
    ".railway.app"
).split(",")

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
    'catering',
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
        # FIX: We use BASE_DIR.parent to step out of 'backend' and find 'templates'
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
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=True
        )
    }
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
    BASE_DIR.parent / 'static',
]

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS
CORS_ALLOW_ALL_ORIGINS = True

# Rest Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
}

# --- EMAIL SETTINGS (SMTP) ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'swagatcaterersofficial@gmail.com'
EMAIL_HOST_PASSWORD = 'cqib xpwa cxwo mtri'  # App Password
DEFAULT_FROM_EMAIL = 'swagatcaterersofficial@gmail.com'

# Custom User & Auth
AUTH_USER_MODEL = 'catering.User'
AUTHENTICATION_BACKENDS = [
    'catering.backends.EmailPhoneUsernameBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Djoser
DJOSER = {
    'SERIALIZERS': {
        'user_create': 'catering.serializers.UserCreateSerializer',
        'user': 'catering.serializers.UserSerializer',
        'current_user': 'catering.serializers.UserSerializer',
    },
}

SITE_URL = "https://swagatcaterers.in"

# Media Files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'