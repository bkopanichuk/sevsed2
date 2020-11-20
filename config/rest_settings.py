REST_FRAMEWORK = {
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser'
        # ...
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer'
    ),
    'DEFAULT_METADATA_CLASS': 'apps.l_core.metadata.LCoreSimpleMetadata',

    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_PAGINATION_CLASS': 'apps.l_core.pagination.LCOREPagination',
    'PAGE_SIZE': 5,

    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        # 'sync_client.authentication.SyncClientAuthentication',
    ),
    'UNAUTHENTICATED_USER': 'django.contrib.auth.models.AnonymousUser',
    'DEFAULT_PERMISSION_CLASSES': [
        ##'rest_framework.permissions.AllowAny',
        'rest_framework.permissions.IsAuthenticated',
        ##'rest_framework.permissions.DjangoModelPermissions',
        ##'l_core.permissions.LCoreDjangoModelPermissions',
    ],
}

REST_REGISTRATION = {
    'REGISTER_VERIFICATION_ENABLED': False,
    'REGISTER_EMAIL_VERIFICATION_ENABLED': False,
    'RESET_PASSWORD_VERIFICATION_ENABLED': False,
}
