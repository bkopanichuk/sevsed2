CELERY_TIMEZONE = 'UTC'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
#CELERY_CREATE_DIRS=1

CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'default'##Ключ кеша з довідника CACHES