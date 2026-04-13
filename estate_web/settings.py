from pathlib import Path
import os
from decouple import config, Csv


# =============================================================================
# PATHS
# =============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# =============================================================================
# CORE SECURITY
# =============================================================================

SECRET_KEY = config('SECRET_KEY')
ADMIN_SECRET_PATH = config('ADMIN_SECRET_PATH')
DJANGO_ADMIN_PATH = config('DJANGO_ADMIN_PATH')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

CSRF_TRUSTED_ORIGINS = [
    'https://estate-web-sufx.onrender.com',
    'https://estatewebng.com',
    'https://www.estatewebng.com',
]




# =============================================================================
# APPLICATIONS
# =============================================================================

INSTALLED_APPS = [
    # Django core
    'axes',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sites',

    # Estate Web apps
    'estate',
    'members',
    'admin_panel',
    'agents',
    'companies',
    'landlord',
    'core',

    # Third-party
    'widget_tweaks',
    'django_filters',
    'cloudinary',
    'cloudinary_storage',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]


# =============================================================================
# MIDDLEWARE
# =============================================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]


# =============================================================================
# URL / WSGI
# =============================================================================

ROOT_URLCONF = 'estate_web.urls'
WSGI_APPLICATION = 'estate_web.wsgi.application'
SITE_ID = 1


# =============================================================================
# TEMPLATES
# =============================================================================

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
                'core.context_processors.base_template',
            ],
        },
    },
]


# =============================================================================
# DATABASE
# =============================================================================

if config('USE_DB', cast=bool):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': config('DB_NAME'),
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default=5432, cast=int),
            'CONN_MAX_AGE': 60,
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# =============================================================================
# AUTHENTICATION
# =============================================================================

AUTH_USER_MODEL = 'members.User'

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',          # must be first
    'members.backends.EmailOrUsernameModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LOGIN_URL = 'login'
LOGOUT_URL = 'logout'
LOGIN_REDIRECT_URL = 'landing'
PASSWORD_RESET_TIMEOUT = 3600
ALLAUTH_TRUSTED_PROXY_COUNT = 1
ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = True


# =============================================================================
# DJANGO-AXES (Brute Force Protection)
# =============================================================================

AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1                                   # hours
AXES_LOCKOUT_PARAMETERS = ['ip_address', 'username']
AXES_LOCKOUT_CALLABLE = 'core.views.lockout_response'


# =============================================================================
# ALLAUTH
# =============================================================================

ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGOUT_REDIRECT_URL = 'landing'
ACCOUNT_EMAIL_VERIFICATION_MAX_RESEND_COUNT = 2
ACCOUNT_EMAIL_VERIFICATION_MAX_CHANGE_COUNT = 2  # Allow up to 2 changes
ACCOUNT_NOTIFY_ON_PASSWORD_CHANGE = True


# settings.py
ACCOUNT_RATE_LIMITS = {
    # For code-based: max 1 per 10 seconds per email
    "confirm_email": "1/10s/key",
    
    # For link-based: max 1 per 3 minutes per email
    # Controlled by ACCOUNT_EMAIL_CONFIRMATION_COOLDOWN
}
ACCOUNT_RATE_LIMITS = {
    "confirm_email": "1/2m/key",  # 1 confirmation per 2 minutes per key
}


# settings.py
# =============================================================================
# GOOGLE OAUTH
# =============================================================================

SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_EMAIL_VERIFICATION = "none"
SOCIALACCOUNT_ADAPTER = 'allauth.socialaccount.adapter.DefaultSocialAccountAdapter'
# Add this to allow linking existing users by email
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_LOGIN_ON_GET = True
SOCIALACCOUNT_ADAPTER = 'members.adapter.MySocialAccountAdapter'
ACCOUNT_ADAPTER = 'members.adapter.MyAccountAdapter'
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'offline'},
        'OAUTH_PKCE_ENABLED': True,
    }
}


# =============================================================================
# EMAIL — Zoho ZeptoMail
# =============================================================================

EMAIL_BACKEND = 'zoho_zeptomail.backend.zeptomail_backend.ZohoZeptoMailEmailBackend'
ZOHO_ZEPTOMAIL_API_KEY_TOKEN = config('ZEPTOMAIL_API_TOKEN')
ZOHO_ZEPTOMAIL_HOSTED_REGION = 'zeptomail.zoho.com'
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='Estate Web <no-reply@estatewebng.com>')
EMAIL_PORT=587

# =============================================================================
# STATIC FILES
# =============================================================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

if DEBUG:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
else:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# =============================================================================
# MEDIA FILES & CLOUDINARY
# =============================================================================

USE_CLOUDINARY = config('USE_CLOUDINARY', cast=bool)

if USE_CLOUDINARY:
    CLOUDINARY_CLOUD_NAME = config('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = config('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = config('CLOUDINARY_API_SECRET')

    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': CLOUDINARY_CLOUD_NAME,
        'API_KEY': CLOUDINARY_API_KEY,
        'API_SECRET': CLOUDINARY_API_SECRET,
    }

    STORAGES = {
        'default': {'BACKEND': 'cloudinary_storage.storage.MediaCloudinaryStorage'},
        'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
    }
else:
    # Local dev fallback
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# =============================================================================
# CACHE
# =============================================================================
if not DEBUG:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
            'LOCATION': 'cache_table',
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }

RATELIMIT_VIEW = 'core.views.ratelimit_error'


# =============================================================================
# SESSION & COOKIE SECURITY
# =============================================================================

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 1209600        # 2 weeks in seconds








CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax' 
X_FRAME_OPTIONS = 'DENY'


# =============================================================================
# HTTPS / SSL (toggled by DEBUG)
# =============================================================================

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
else:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_HSTS_SECONDS = 0
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False


# =============================================================================
# INTERNATIONALISATION
# =============================================================================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Lagos'
USE_I18N = True
USE_TZ = True


# =============================================================================
# RATE LIMITING CACHES
# =============================================================================

#TODO add the one for production