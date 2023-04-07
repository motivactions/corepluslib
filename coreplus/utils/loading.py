from importlib import import_module

from django.apps import apps
from django.apps.config import MODELS_MODULE_NAME
from django.core.exceptions import AppRegistryNotReady
from django.utils.module_loading import module_has_submodule


def extract_contenttype(contenttype_format):
    contenttype_id, app_name, model_name = contenttype_format.split(".")
    result = dict()
    result["model_name"] = model_name
    result["contenttype_model"] = apps.get_model(app_name, model_name)
    result["contenttype_slug"] = ".".join([app_name, model_name])
    result["contenttype_id"] = contenttype_id
    result["app_name"] = app_name
    return result


def get_app_modules():
    """
    Generator function that yields a module object for each installed app
    yields tuples of (app_name, module)
    """
    for app in apps.get_app_configs():
        yield app.name, app.module


def get_app_submodules(submodule_name):
    """
    Searches each app module for the specified submodule
    yields tuples of (app_name, module)
    """
    for name, module in get_app_modules():
        if module_has_submodule(module, submodule_name):
            yield name, import_module("%s.%s" % (name, submodule_name))


def get_model(app_label, model_name):
    """
    Fetches a Django model using the app registry.

    This doesn't require that an app with the given app label exists,
    which makes it safe to call when the registry is being populated.
    All other methods to access models might raise an exception about the
    registry not being ready yet.
    Raises LookupError if model isn't found.
    """
    try:
        return apps.get_model(app_label, model_name)
    except AppRegistryNotReady:
        if apps.apps_ready and not apps.models_ready:
            # If this function is called while `apps.populate()` is
            # loading models, ensure that the module that defines the
            # target model has been imported and try looking the model up
            # in the app registry. This effectively emulates
            # `from path.to.app.models import Model` where we use
            # `Model = get_model('app', 'Model')` instead.
            app_config = apps.get_app_config(app_label)
            # `app_config.import_models()` cannot be used here because it
            # would interfere with `apps.populate()`.
            import_module("%s.%s" % (app_config.name, MODELS_MODULE_NAME))
            # In order to account for case-insensitivity of model_name,
            # look up the model through a private API of the app registry.
            return apps.get_registered_model(app_label, model_name)
        else:
            # This must be a different case (e.g. the model really doesn't
            # exist). We just re-raise the exception.
            raise


def is_model_registered(app_label, model_name):
    """
    Checks whether a given model is registered. This is used to only
    register models if they aren't overridden by a forked app.
    """
    try:
        apps.get_registered_model(app_label, model_name)
    except LookupError:
        return False
    else:
        return True
