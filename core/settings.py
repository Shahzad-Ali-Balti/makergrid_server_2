from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# Main app uses this for generating URLs to media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'





# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

FRONTEND_DOMAIN = os.getenv('FRONTEND_DOMAIN') or "http://localhost:5173" or "https://www.makergrid.ai"
NGROK_DOMAIN = os.getenv("NGROK_DOMAIN") or "03b6-203-175-73-87.ngrok-free.app"
# ALLOWED_HOSTS = [] 
# ALLOWED_HOSTS = ["localhost", "127.0.0.1",NGROK_DOMAIN,"http://makergrids.eba-muuyvbmf.eu-north-1.elasticbeanstalk.com/"]
# settings.py
ALLOWED_HOSTS = ['*', 'ec2-51-20-127-221.eu-north-1.compute.amazonaws.com']


# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
    "rest_framework",
    "community",
    "makers",
    "corsheaders",
    'django_celery_beat',

]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    'makers.middleware.NewAccessTokenMiddleware'
]

CORS_ALLOWED_ORIGINS = [
    FRONTEND_DOMAIN
]
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
    FRONTEND_DOMAIN
]

#REMOVE IT WHEN PRODUCTION ------- WARNING
CORS_ALLOW_ALL_ORIGINS = True
#REMOVE IT WHEN PRODUCTION ------- WARNING

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'range',  # <-- important if partial file requests are made
]


ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"
ASGI_APPLICATION = "core.asgi.application"  # replace with your project name

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/
STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.AllowAny",
    ),
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ),
}

AUTH_USER_MODEL = "accounts.CustomUser"

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),  # ⏰ Change this to what you want
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),     # You can customize this too

    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
}
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'console': {
#             'class': 'logging.StreamHandler',
#         },
#     },
#     'root': {
#         'handlers': ['console'],
#         'level': 'DEBUG',  # <- ensure this is DEBUG
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['console'],
#             'level': 'DEBUG',  # <- also enable DEBUG for django
#             'propagate': True,
#         },
#     },
# }
STATIC_ROOT = "/static/"
STATIC_URL = "/static/"


CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
        
    }
}

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# settings.py

STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")



CELERY_BROKER_URL = 'memory://'
CELERY_RESULT_BACKEND = 'cache+memory://'
CELERY_TASK_ALWAYS_EAGER = True  # Optional: set True to run tasks immediately (for testing)
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'


AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')  # Your AWS access key ID
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')  # Your AWS secret access key
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')  # Your S3 bucket name
AWS_S3_REGION_NAME = 'us-east-1'  # Your S3 region (e.g., us-east-1)
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_DEFAULT_ACL = None  # To ensure files are uploaded as private


aws_lambda_s3_key=os.getenv('aws_lambda_s3_api_key')