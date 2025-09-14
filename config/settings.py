import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Core Settings ---
SECRET_KEY = os.getenv('SECRET_KEY', 'a-strong-dev-secret-key-that-is-long')
# DEBUG is False by default on Railway, True if you set DEBUG=True
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# --- Railway Deployment Settings ---
# This is the most important security setting.
ALLOWED_HOSTS = []
CSRF_TRUSTED_ORIGINS = []

RAILWAY_STATIC_URL = os.environ.get('RAILWAY_STATIC_URL')
if RAILWAY_STATIC_URL:
    # Add the Railway URL to both settings
    ALLOWED_HOSTS.append(RAILWAY_STATIC_URL)
    CSRF_TRUSTED_ORIGINS.append(f"https://{RAILWAY_STATIC_URL}")
else:
    # Allow local development hosts if not on Railway
    ALLOWED_HOSTS.extend(['127.0.0.1', 'localhost'])

# --- Application Definition ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware", # Whitenoise should be second
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'core' / 'templates'],
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

# --- Database ---
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
# NOTE: For production, you should add a PostgreSQL database in Railway.
# The DATABASE_URL will be set automatically. SQLite data is deleted on each deploy.
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR}/db.sqlite3",
        conn_max_age=600
    )
}

# --- Password Validation ---
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- Internationalization ---
# https://docs.djangoproject.com/en/4.2/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# --- Static files (CSS, JavaScript, Images) ---
# https://docs.djangoproject.com/en/4.2/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# --- Media Files ---
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / '.media'

# --- App Specific Settings ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'core.User'
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'core.auth_backend.PhoneOrUsernameBackend',
]

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# --- Google Drive Config ---
GDRIVE_SERVICE_ACCOUNT_FILE = os.getenv('GDRIVE_SERVICE_ACCOUNT_FILE', '')
if GDRIVE_SERVICE_ACCOUNT_FILE:
    gdrive_path = Path(GDRIVE_SERVICE_ACCOUNT_FILE)
    if not gdrive_path.is_absolute():
        gdrive_path = BASE_DIR / gdrive_path
    
    from google.oauth2 import service_account
    GOOGLE_DRIVE_CREDENTIALS = service_account.Credentials.from_service_account_file(
        str(gdrive_path),
        scopes=['https://www.googleapis.com/auth/drive.file']
    )
else:
    GOOGLE_DRIVE_CREDENTIALS = None