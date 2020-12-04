import os

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'sed_test_db_5',
        'HOST': 'localhost',
        'PORT': '5432',
        'USER': 'sed_user',
        'PASSWORD': 'sed_user',
    },
    # # LOG
    'logs': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'logs',
        'HOST': 'localhost',
        'PORT': '5432',
        'USER': 'sed',
        'PASSWORD': 'sed',
    }
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    #     'USER': '',
    #     'PASSWORD': '',
    #     'HOST': '',  # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
    #     'PORT': '',
    # }
}