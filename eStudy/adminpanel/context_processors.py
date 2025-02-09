import random
from django.apps import apps
from courses.models import *

def models_name(request):
    user_model_info = {
        'name': User.__name__,
        'app_label': User._meta.app_label,
        'verbose_name': User._meta.verbose_name_plural,
    }

    custom_models_info = []
    for app_config in apps.get_app_configs():
        if not app_config.name.startswith('django.') and app_config.name != 'adminpanel':
            for model in app_config.get_models():
                custom_models_info.append({
                    'name': model.__name__,
                    'app_label': model._meta.app_label,
                    'verbose_name': model._meta.verbose_name_plural,
                })
    models = custom_models_info

    return {'models_list': models}
