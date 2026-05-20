import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-voltwatch-ai-dev-key")
DEBUG = os.environ.get("DJANGO_DEBUG", "True").lower() == "true"
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "monitoring",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "voltwatch.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [],
        },
    },
]

WSGI_APPLICATION = "voltwatch.wsgi.application"

# No database required: stateless app, browser localStorage persistence only.
DATABASES = {}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
