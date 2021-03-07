"""
Django settings for alexandria project.

Generated by 'django-admin startproject' using Django 2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", '*qn*8fffxcth7jfb#&_r0w%9d!l2x(6nbge*d5*rapbufw=+-5')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'alexandrialibrary.dev', '.alexandrialibrary.dev', '192.168.1.185', 'localhost'
]


AUTH_USER_MODEL = "users.AlexandriaUser"
LOGIN_URL = '/login/'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "widget_tweaks",
    "taggit",
    "general",
    "users",
    "localflavor",
    "catalog",
    "holds",
    "payments",
    "selfcheckout",
    "staff",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'alexandria.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates")],
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

WSGI_APPLICATION = 'alexandria.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

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


# Customizations

# used for the default keys in address fields when signing up a user -- change
# these to match the area that this is deployed in
DEFAULT_ADDRESS_STATE_OR_REGION = "IN"
DEFAULT_ADDRESS_CITY = "Indianapolis"
DEFAULT_ADDRESS_ZIP_CODE = "46227"
DEFAULT_ADDRESS_COUNTRY = "USA"

# keep track of how much patrons have saved by using the library; this is a
# privacy-centric value that only tallies the total value of the books on their
# account as a single integer.
ENABLE_RUNNING_BORROW_SAVED_MONEY = True

# Enable this if no material has a home branch location.
FLOATING_COLLECTION = False
FORCE_UNIQUE_CALL_NUMBERS = False
LIBRARY_SYSTEM_NAME = "Alexandria Libraries"
LIBRARY_SYSTEM_URL = "https://github.com/AlexandriaILS/Alexandria"

# When adding new materials, the home location will default to a single place
# until it can be edited. Usually this is the first place that's added when
# the system is first configured, but if it's not then just set the ID of the
# target location here. For example, if the ID of a processing center is #3,
# then you'd set a 3 here.
DEFAULT_LOCATION_ID = 1

IGNORED_SEARCH_TERMS = ["a", "an", "the"]
DEFAULT_RESULTS_PER_PAGE = 25

# The base URL and configuration settings for Zenodotus, the head librarian
# service for Alexandria. It keeps copies of base Records to speed up importing
# and to serve as a backup. Downloading is always available, and uploading is
# optional (but recommended) -- it helps out other users of Alexandria!
ZENODOTUS_URL = "https://zenodotus.alexandrialibrary.dev/api/"
ZENODOTUS_AUTO_UPLOAD = True
