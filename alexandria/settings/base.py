"""
Django settings for alexandria project.

Generated by 'django-admin startproject' using Django 2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

from collections.abc import Mapping
import os
import subprocess

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

try:
    CURRENT_HASH = (
        subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
        .decode("utf-8")
        .strip()
    )
except subprocess.CalledProcessError:
    CURRENT_HASH = "unknown version"

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY", "*qn*8fffxcth7jfb#&_r0w%9d!l2x(6nbge*d5*rapbufw=+-5"
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# actual validation handled in middleware
ALLOWED_HOSTS = ["*"]
# used for handling configs on the request
DEFAULT_HOSTS = ["localhost:8000", "staging.alexandrialibrary.dev"]
INTERNAL_IPS = [
    "localhost",
    "127.0.0.1",
]
DEFAULT_HOST_KEY = "default"
DEFAULT_SYSTEM_HOST_KEY = "system"


class LazySiteData(Mapping):
    # from https://stackoverflow.com/a/47212782 with minor tweaks
    def __init__(self, *args, **kw):
        self._raw_dict = dict(*args, **kw)

    def __getitem__(self, key):
        if not self._raw_dict:
            self.init_data()
        return self._raw_dict.__getitem__(key)

    def __iter__(self):
        if not self._raw_dict:
            self.init_data()
        return iter(self._raw_dict)

    def __len__(self):
        if not self._raw_dict:
            self.init_data()
        return len(self._raw_dict)

    def init_data(self):
        from alexandria.distributed.configs import init_site_data

        self._raw_dict = init_site_data()


SITE_DATA = LazySiteData()  # this will get populated at runtime

AUTH_USER_MODEL = "users.User"
LOGIN_URL = "/login/"
CSRF_TRUSTED_ORIGINS = [
    "https://" + entry for entry in DEFAULT_HOSTS if not "localhost" in entry
]

# Application definition

INSTALLED_APPS = [
    # internal
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    # third party
    "debug_toolbar",
    "anymail",
    "localflavor",
    "mathfilters",
    "widget_tweaks",
    "slippers",
    "taggit",
    "rest_framework",
    # first party
    "alexandria.api",
    "alexandria.searchablefields",
    "alexandria.distributed",
    "alexandria.utils",
    "alexandria.integrations",
    "alexandria.users",
    "alexandria.records",
    "alexandria.catalog",
    "alexandria.money",
]

MIDDLEWARE = [
    "django.middleware.gzip.GZipMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "alexandria.distributed.middleware.HostValidationMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "alexandria.distributed.middleware.ContextUpdateMiddleware",
]

ROOT_URLCONF = "alexandria.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "builtins": ["slippers.templatetags.slippers"],
        },
    },
]

WSGI_APPLICATION = "alexandria.wsgi.application"

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

MEDIA_ROOT = os.path.join(BASE_DIR, "images")
MEDIA_URL = "/media/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static_dev")]
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

ANYMAIL = {
    "MAILGUN_API_KEY": "EXAMPLE",
    "MAILGUN_SENDER_DOMAIN": "EXAMPLE",
}

# EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"

# for testing by writing files
EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_FILE_PATH = os.path.join(BASE_DIR, "sent_emails")

DEFAULT_FROM_EMAIL = "no-reply@alexandrialibraries.dev"
SERVER_EMAIL = "thefabled@alexandrialibraries.dev"

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25
}
