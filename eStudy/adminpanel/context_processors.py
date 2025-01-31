import random
from django.apps import apps
from courses.models import *

def models_name(request):
    # Get the default User model
    user_model_info = {
        'name': User.__name__,
        'app_label': User._meta.app_label,
        'verbose_name': User._meta.verbose_name_plural,
    }

    # Get all models from your custom apps
    custom_models_info = []
    for app_config in apps.get_app_configs():
        # Exclude Django's built-in apps (e.g., admin, auth, sessions)
        if not app_config.name.startswith('django.') and app_config.name != 'adminpanel':
            for model in app_config.get_models():
                custom_models_info.append({
                    'name': model.__name__,
                    'app_label': model._meta.app_label,
                    'verbose_name': model._meta.verbose_name_plural,
                })

    # Combine the User model and custom app models
    models = custom_models_info

    return {'models_list': models}
