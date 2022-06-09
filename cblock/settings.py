
"""
Django settings for cblock project.

Generated by 'django-admin startproject' using Django 3.2.9.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
from .config import config
from .logging_settings import LOGGING
import logging.config
import os

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
logging.config.dictConfig(LOGGING)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config.secret_key
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config.debug

ALLOWED_HOSTS = config.allowed_hosts

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django_extensions',
    'drf_yasg',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_auth',
    'rest_auth.registration',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'django_dramatiq',
    'cblock.accounts',
    'cblock.contracts',
    'cblock.scheduler',
    'cblock.rates',
    'scanner',
]
PRE_MIDDLEWARES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
]

CSRF_MIDDLEWARE = 'django.middleware.csrf.CsrfViewMiddleware'
TEST_CSRF_MIDDLEWARE = 'cblock.utils.DisableCSRF'

POST_MIDDLEWARES = [
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


SET_CSRF_MIDDLEWARE = [TEST_CSRF_MIDDLEWARE if config.debug else CSRF_MIDDLEWARE]

MIDDLEWARE = PRE_MIDDLEWARES + SET_CSRF_MIDDLEWARE + POST_MIDDLEWARES

ROOT_URLCONF = 'cblock.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'cblock.wsgi.application'

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
#    'DEFAULT_PERMISSION_CLASSES': (
 #       'rest_framework.permissions.IsAuthenticated',
  #  ),
}

REST_AUTH_REGISTER_SERIALIZERS = {
    'REGISTER_SERIALIZER': 'cblock.accounts.serializers.MetamaskRegisterSerializer',
}

REST_AUTH_SERIALIZERS = {
    'USER_DETAILS_SERIALIZER': 'cblock.accounts.serializers.MetamaskUserSerializer',
    'PASSWORD_RESET_SERIALIZER': 'cblock.accounts.serializers.CustomDomainPasswordResetSerializer'
}

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'wish'),
        'USER': os.getenv('POSTGRES_USER', 'wish'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'wish'),
        'HOST': os.getenv('POSTGRES_HOST', 'db'),
        'PORT': '5432',
    },
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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

ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
AUTH_USER_MODEL = 'accounts.Profile'
ACCOUNT_ADAPTER = 'cblock.accounts.adapters.CustomDomainAdapter'
SITE_ID = 1

# if config.debug:
#     SESSION_COOKIE_HTTPONLY = False
#     CSRF_COOKIE_HTTPONLY = False

if config.frontend_host_domain:
    # SESSION_COOKIE_DOMAIN = config.frontend_host_domain
    # CSRF_COOKIE_DOMAIN = config.frontend_host_domain
    SESSION_COOKIE_SAMESITE = 'None'
    CSRF_COOKIE_SAMESITE = 'None'
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True

CSRF_TRUSTED_ORIGINS =  config.allowed_hosts

LOGIN_URL = '/'
LOGIN_REDIRECT_URL = LOGIN_URL
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = '/confirm-email'
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL

OLD_PASSWORD_FIELD_ENABLED = True
LOGOUT_ON_PASSWORD_CHANGE = False


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

SHELL_PLUS = 'ptpython'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = config.static_url
STATIC_ROOT = os.path.join(BASE_DIR, config.static_root)

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
EMAIL_HOST = config.email_host
EMAIL_HOST_USER = config.email_host_user
EMAIL_HOST_PASSWORD = config.email_password
EMAIL_PORT = config.email_port

DEFAULT_FROM_EMAIL = config.email_host_user

# dramatiq
DRAMATIQ_BROKER = {
    "BROKER": "dramatiq.brokers.redis.RedisBroker",
    "OPTIONS": {
        "url": f"redis://{config.redis_host}:{config.redis_port}",
    },
    "MIDDLEWARE": [
        "dramatiq.middleware.AgeLimit",
        "dramatiq.middleware.TimeLimit",
        "dramatiq.middleware.Callbacks",
        "dramatiq.middleware.Retries",
        "django_dramatiq.middleware.DbConnectionsMiddleware",
    ]
}

if config.sentry_dsn:
    sentry_sdk.init(
        dsn=config.sentry_dsn,
        integrations=[DjangoIntegration()],

        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        # send_default_pii=True
        traces_sample_rate=1.0
    )
