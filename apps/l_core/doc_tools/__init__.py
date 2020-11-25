from django.apps import apps as global_apps
from django.db import DEFAULT_DB_ALIAS, router


def get_comments_for_model(model, show_empty=None):
    column_comments = []
    for field in model._meta.fields:
        comment = {}
        # Check if verbose name was not autogenerated, according to django code
        # https://github.com/django/django/blob/9681e96/django/db/models/fields/__init__.py#L724
        if field.verbose_name.lower() != field.name.lower().replace('_', ' '):
            comment['verbose_name'] = (str(field.verbose_name))  # str() is workaround for Django.ugettext_lazy

        comment['required'] = 'Так' if field.null else 'Ні'
        # if field.default:
        #     comment['default'] = field.get_default()

        if field.help_text:
            comment['help_text'] = (str(field.help_text))  # str() is workaround for Django.ugettext_lazy
        if comment or show_empty:
            comment['column'] = field.column
            comment['data_type'] = field.get_internal_type()
            column_comments.append(comment)
    return column_comments


def get_help_text_from_apps(apps=global_apps, apps_to_doc=None):
    # if not app_config.models_module:
    #     return
    #
    #
    # app_label = app_config.label
    # if not router.allow_migrate(using, app_label):
    #     return
    #
    # app_config = apps.get_app_config(app_label)
    # app_models = app_config.get_models()
    apps_data = []
    for app in apps.get_app_configs():
        ##raise Exception(app.label)
        if not app.label in apps_to_doc:
            continue
        _t = []
        for model in app.get_models():
            tables_comments = {'label': model._meta.verbose_name, 'fields': get_comments_for_model(model)}
            _t.append(tables_comments)
        apps_data.append({'app': app.verbose_name, 'data': _t})
    return apps_data