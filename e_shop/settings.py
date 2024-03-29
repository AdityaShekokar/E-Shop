"""
Django settings for e_shop project.

Generated by 'django-admin startproject' using Django 3.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import logging
import os
import re
from pathlib import Path

import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

logger = logging.getLogger(__name__)
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
APPEND_SLASH = False
env = environ.Env()
app_dir = f"{BASE_DIR}/e_shop/"

if DEBUG:
    env.read_env(env_file=f"{app_dir}.env.dev")  # reading .env.dev file
else:
    env.read_env()  # reading .env file

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str("SECRET_KEY")

ALLOWED_HOSTS = re.split(
    "\s*,\s*", re.sub("^\s+|\s+$", "", env.str("ALLOWED_HOSTS", default="*"))
)

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "store",
    "django_elasticsearch_dsl",
    "users",
    "oauth2_provider",
    "corsheaders",
    "storages",
]

ELASTICSEARCH_DSL = {
    "default": {"hosts": "http://127.0.0.1:9200"},
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "e_shop.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "e_shop.wsgi.application"

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "e_shop",
        "HOST": "127.0.0.1",
        "PORT": "3306",
        "USER": "eshop",
        "PASSWORD": "Password@123",
    },
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

# STATIC_URL = "/static/"
# import os
#
# STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
# MEDIA_URL = "/images/"
# MEDIA_ROOT = BASE_DIR
LOCAL_HOST = env.str("LOCAL_HOST")
AUTH_USER_MODEL = "users.User"
LOGIN_URL = "/admin/login/"

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",  # To keep the Browsable API
    "oauth2_provider.backends.OAuth2Backend",
)

OAUTH2_PROVIDER = {
    # this is the list of available scopes
    "SCOPES": {
        "read": "Read scope",
        "create": "create scope",
        "update": "update scope",
        "delete": "delete scope",
    },
    # access token expire time in seconds.
    "ACCESS_TOKEN_EXPIRE_SECONDS": 31556952,
}
HARD_DELETE_CASCADE = env.str("HARD_DELETE_CASCADE")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(levelname)-8s [%(asctime)s] %(name)s: %(message)s"},
    },
    "handlers": {
        "file": {
            "level": "DEBUG",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": "logging_history.log",
            "when": "D",
            "backupCount": 30,
            "formatter": "standard",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "logging_history.log",
            "formatter": "standard",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": True,
        },
        "store": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": True,
        },
        "users": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": True,
        },
    },
}

## AWS SETUP FOR STATIC AND MEDIA FILES

USE_S3 = env.str("USE_S3") == "TRUE"

if USE_S3:
    AWS_ACCESS_KEY_ID = env.str("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = env.str("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = env.str("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_CUSTOM_DOMAIN = "%s.s3.amazonaws.com" % AWS_STORAGE_BUCKET_NAME
    AWS_S3_OBJECT_PARAMETERS = {
        "CacheControl": "max-age=86400",
    }
    STATICFILES_LOCATION = "static"

    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, "uploads"),
    ]
    STATIC_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, STATICFILES_LOCATION)
    STATICFILES_STORAGE = "e_shop.common.StaticStorage"

    ## aws media

    MEDIAFILES_LOCATION = "media"
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{MEDIAFILES_LOCATION}/"
    DEFAULT_FILE_STORAGE = "e_shop.common.MediaStorage"
    AWS_S3_REGION_NAME = "ap-south-1"
    AWS_S3_ADDRESSING_STYLE = "virtual"
else:
    STATIC_URL = "/staticfiles/"
    STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
    MEDIA_URL = "/mediafiles/"
    MEDIA_ROOT = os.path.join(BASE_DIR, "mediafiles")
