"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 3.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
from django.utils.log import DEFAULT_LOGGING
import logging.config
from .common.djangocolors_formatter import DjangoColorsFormatter
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'xj#nqodwt31!y@78$6w35r_4g#t*a=91ve4z(g76=_*u$$570v'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

from .rest_settings import REST_FRAMEWORK, REST_REGISTRATION
from .email_settings import *
from .cors_settings import *
from .database_settings import DATABASES
from .celery_backend_options import *

# Application definition

INSTALLED_APPS = [
    'admin_interface',
    'colorfield',
    'django.contrib.admin',
    # 'django_select2',
    # 'django_select2_admin_filters',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_auth',
    'rest_registration',
    'django_postgres_createdb',
    'drf_yasg',
    # 'activity_log',
    'apps.atu',
    'apps.l_core.apps.CoreConfig',
    'apps.document.apps.DocumentConfig',
     'apps.contracts.apps.ContractsConfig',
     'apps.client_settings',
    'apps.sevovvintegration.apps.SevovvintegrationConfig',
    'simple_history',
    'preview_generator',
    'django_celery_results',
    'django_celery_beat',
    'silk',
    'apps.uaoauth',
    'multiselectfield',

    # 'sync_client',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'apps.l_core.middleware.PyCallGraphMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
    ##'activity_log.middleware.ActivityLogMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
    'silk.middleware.SilkyMiddleware',
]

ROOT_URLCONF = 'config.urls'

# Default X-Frame-Options header value
X_FRAME_OPTIONS = 'SAMEORIGIN'

USE_X_FORWARDED_HOST = False
USE_X_FORWARDED_PORT = False

AUTH_USER_MODEL = 'l_core.CoreUser'
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

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases


DATABASE_ROUTERS = ['activity_log.router.DatabaseAppsRouter']
DATABASE_APPS_MAPPING = {'activity_log': 'logs'}

REDIS_URL = "redis://127.0.0.1:6379"

CACHES = {
    # … default cache config and others
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL + "/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "select2": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL + "/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

DATA_UPLOAD_MAX_MEMORY_SIZE = 55512000
# Tell select2 which cache configuration to use:
SELECT2_CACHE_BACKEND = "select2"
# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

# AUTH_PASSWORD_VALIDATORS = [
#     {
#         'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
#     },
# ]

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'uk'
# LANGUAGES = (
#     ('en', _('English')),
#     ('uk', _('Ukraine')),
# )

TIME_ZONE = 'Europe/Kiev'

USE_I18N = True

USE_L10N = True

USE_TZ = True

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

MEDIA_URL = '/media/'  # URL для медии в шаблонах

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

ACTIVITYLOG_EXCLUDE_URLS = ('/admin/activity_log/activitylog', '/admin/jsi18n', '/media/admin-interface/')
ACTIVITYLOG_EXCLUDE_STATUSES = (302,)
ACTIVITYLOG_METHODS = ('POST', 'GET')
ACTIVITYLOG_LAST_ACTIVITY = True
ACTIVITYLOG_GET_EXTRA_DATA = 'config.activity_log_extra.make_extra_data'

AUTH_SERVER_CHECK_TOKEN_URL = 'http://10.0.30.220:9999/sync-server/sync-endpoint/'
AUTH_SERVER_SYNC_PERMISSION_URL = 'http://10.0.30.220:9999/sync-server/sync-permissions/'
AUTH_SERVER_MAX_TOKEN_AGE = 40 * 60  ##140 хвилин
AUTH_SERVER_SECRET_KEY = 'sed2'
AUTH_SERVER_CLIENT_ID = 'sed2'

from config.logger import LOGGING
