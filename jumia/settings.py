import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-f6^8ru)l5k0ph81rgny-kgofeb)$o=&e%!nj5ll2^wiqsc(hju'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'e_commerce',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'jumia.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'e_commerce.context_processors.site_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'jumia.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'jumia_db',
        'USER': 'postgres',
        'PASSWORD': 'cp7kvt',
        'HOST': 'localhost',
        'PORT': '5432',
        
    }
}

AUTH_USER_MODEL = 'e_commerce.User'

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')



# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Email Configuration (for production)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# For production:
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'

# Security Settings (for production)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True


# M-Pesa Credentials (Get from Safaricom Daraja Portal)
MPESA_ENVIRONMENT = 'sandbox'  # or 'production'

# Sandbox credentials
MPESA_CONSUMER_KEY = 'your_consumer_key_here'
MPESA_CONSUMER_SECRET = 'your_consumer_secret_here'
MPESA_SHORTCODE = 'your_shortcode_here'  # Usually 174379 for sandbox
MPESA_PASSKEY = 'your_passkey_here'

# API Endpoints
if MPESA_ENVIRONMENT == 'sandbox':
    MPESA_AUTH_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    MPESA_STK_PUSH_URL = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
    MPESA_QUERY_URL = 'https://sandbox.safaricom.co.ke/mpesa/stkpushquery/v1/query'
else:
    MPESA_AUTH_URL = 'https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    MPESA_STK_PUSH_URL = 'https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
    MPESA_QUERY_URL = 'https://api.safaricom.co.ke/mpesa/stkpushquery/v1/query'

# Callback URL (must be publicly accessible)
# For local testing, use ngrok: https://ngrok.com
MPESA_CALLBACK_URL = 'https://your-domain.com/payment/mpesa/callback/'

# For local development with ngrok:
# 1. Install ngrok: https://ngrok.com/download
# 2. Run: ngrok http 8000
# 3. Copy the https URL and append /payment/mpesa/callback/
# Example: https://abc123.ngrok.io/payment/mpesa/callback/