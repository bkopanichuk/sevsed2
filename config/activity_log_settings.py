ACTIVITYLOG_AUTOCREATE_DB = False
DATABASE_APPS_MAPPING = {'activity_log': 'logs'}
ACTIVITYLOG_ANONIMOUS = True
ACTIVITYLOG_EXCLUDE_URLS = ('/admin/activity_log/activitylog', '/admin/jsi18n', '/media/admin-interface/')
ACTIVITYLOG_EXCLUDE_STATUSES = (302,)
ACTIVITYLOG_METHODS = ('POST', 'GET','PUT','PUSH','DELETE')
ACTIVITYLOG_LAST_ACTIVITY = True
##ACTIVITYLOG_GET_EXTRA_DATA = 'config.activity_log_extra.make_extra_data'