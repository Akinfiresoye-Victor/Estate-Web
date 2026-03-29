from pathlib import Path
import os
from decouple import config, Csv
import dj_database_url
import cloudinary_storage



# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

CSRF_TRUSTED_ORIGINS = [
    'https://estate-web-sufx.onrender.com',
    'https://estatewebng.com',
    'https://www.estatewebng.com',
]




AUTH_USER_MODEL = 'members.User'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',  # REQUIRED
        'DIRS': [],  # You can add any custom template directories here
        'APP_DIRS': True,  # Important: looks for templates inside each app
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # REQUIRED for admin
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.base_template',
            ],
        },
    },
]


# Applications
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'estate',
    'members',
    'admin_panel',
    'agents',
    'companies',
    'core',
    'widget_tweaks',
    'django_filters',
    'cloudinary',
    'cloudinary_storage',
    'django.contrib.humanize',
    'axes',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Serves static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'estate_web.urls'
WSGI_APPLICATION = 'estate_web.wsgi.application'

# Database (Postgres with decouple)
if config('USE_DB', cast=bool):
    print('active/original db is active')
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": config('DB_NAME'),
            "USER": config('DB_USER'),
            "PASSWORD": config('DB_PASSWORD'),
            "HOST": config('DB_HOST', default='localhost'),
            "PORT": config('DB_PORT', default=5432, cast=int),
        }
    }
else:
    print('Default db is active')
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }




EMAIL_BACKEND = 'zoho_zeptomail.backend.zeptomail_backend.ZohoZeptoMailEmailBackend'
ZOHO_ZEPTOMAIL_API_KEY_TOKEN = config('ZEPTOMAIL_API_TOKEN')
ZOHO_ZEPTOMAIL_HOSTED_REGION = 'zeptomail.zoho.com' 
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'offline',
        },
        'OAUTH_PKCE_ENABLED': True,
    }
}

LOGIN_URL = 'login'
LOGOUT_URL='logout'
ACCOUNT_LOGOUT_REDIRECT_URL = 'landing'
LOGIN_REDIRECT_URL = 'landing'
# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

#TODO set up password warning and forget password functinality
AXES_FAILURE_LIMIT = 5        # lock after 5 failed attempts
AXES_COOLOFF_TIME  = 1        # lock for 1 hour
AXES_LOCKOUT_PARAMETERS = ['ip_address', 'username']  # lock by IP and username
PASSWORD_RESET_TIMEOUT = 3600
# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Lagos'
USE_I18N = True
USE_TZ = True

# Static & media files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # For collectstatic
# STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
if DEBUG:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
else:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'




# Cloudinary credentials via environment variables





# Only use Cloudinary storage in production (recommended)
USE_CLOUDINARY = config('USE_CLOUDINARY', cast=bool)
print(f'Cloud media active?> {USE_CLOUDINARY}')
# Default primary key field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



if USE_CLOUDINARY:
    CLOUDINARY_CLOUD_NAME = config('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = config('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = config('CLOUDINARY_API_SECRET')

    CLOUDINARY_STORAGE={
        'CLOUD_NAME':CLOUDINARY_CLOUD_NAME,
        'API_KEY': CLOUDINARY_API_KEY,
        'API_SECRET': CLOUDINARY_API_SECRET,
    }

    STORAGES = {
        "default": {"BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage"},
        "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
    }

else:

# Local dev fallback (your existing media settings)
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


SESSION_COOKIE_HTTPONLY = True   # JS cannot read the cookie
SESSION_COOKIE_SAMESITE = 'Lax'  # blocks cross-site request cookie leaks
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 1209600     # 2 weeks in seconds

# Clickjacking protection
X_FRAME_OPTIONS = 'DENY'


# Cookie security
CSRF_COOKIE_HTTPONLY    = True


# --- SECURE SETTINGS ---
if not DEBUG:
    # Production Settings (Keep these for Render/VPS)
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000 
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
else:
    # Local Development Settings
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_HSTS_SECONDS = 0
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False

print('Debug Mode>', DEBUG)
SITE_ID = 1
SOCIALACCOUNT_LOGIN_ON_GET = True
SOCIALACCOUNT_ADAPTER = 'members.adapter.MySocialAccountAdapter'