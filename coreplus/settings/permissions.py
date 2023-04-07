from django.apps import apps
from django.db import models


def user_can_edit_any_settings(user):
    from .registries import registry

    perms = any([user_can_edit_setting_type(user, model) for model in registry])
    return perms


def get_model(model):
    if isinstance(model, models.Model):
        model = model
    elif isinstance(model, str):
        model = apps.get_model(model)


def get_perm_name(model):
    name = "{}.change_{}".format(
        model._meta.app_label,
        model._meta.model_name,
    )
    return name


def get_settings_perm_names():
    from .registries import registry

    perm_names = [get_perm_name(m) for m in registry]
    return perm_names


def user_can_edit_setting(user, model=None):
    if model is None:
        return user.has_perms(get_settings_perm_names())
    if isinstance(model, (list, tuple, set)):
        model = [get_model(m) for m in model]
    else:
        model[get_model(model)]
    perms = [get_perm_name(m) for m in model]
    return user.has_perms(perms)


def user_can_edit_setting_type(user, model):
    """Check if a user has permission to edit this setting type"""
    return user.has_perm(
        "{}.change_{}".format(
            model._meta.app_label,
            model._meta.model_name,
        ),
    )
