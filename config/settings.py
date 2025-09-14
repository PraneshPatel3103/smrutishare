
import os
from pathlib import Path
from dotenv import load_dotenv
import os
import dj_database_url

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ["*"]  # or ["your-app-name.up.railway.app"]


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
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = os.getenv('MEDIA_URL', '/media/')
MEDIA_ROOT = Path(os.getenv('MEDIA_ROOT', BASE_DIR / '.media'))

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'core.User'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'core.auth_backend.PhoneOrUsernameBackend',
]

# Google Drive config (optional)
GDRIVE_SERVICE_ACCOUNT_FILE = os.getenv('GDRIVE_SERVICE_ACCOUNT_FILE', '')

if GDRIVE_SERVICE_ACCOUNT_FILE:
    from pathlib import Path
    from google.oauth2 import service_account

    gdrive_path = Path(GDRIVE_SERVICE_ACCOUNT_FILE)

    # if relative, resolve against BASE_DIR
    if not gdrive_path.is_absolute():
        gdrive_path = BASE_DIR / gdrive_path

    GDRIVE_SERVICE_ACCOUNT_FILE = gdrive_path

    GOOGLE_DRIVE_CREDENTIALS = service_account.Credentials.from_service_account_file(
        str(GDRIVE_SERVICE_ACCOUNT_FILE),
        scopes=['https://www.googleapis.com/auth/drive.file']
    )
else:
    GOOGLE_DRIVE_CREDENTIALS = None


LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
DATABASES = {
    "default": dj_database_url.config(default="sqlite:///db.sqlite3")
}
