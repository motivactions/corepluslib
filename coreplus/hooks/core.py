from importlib import import_module
from operator import itemgetter

from django.apps import apps
from django.utils.module_loading import module_has_submodule

from ..configs import coreplus_configs as configs

_corehook = {}
_searched_for_corehook = False


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


def register(hook_name, fn=None, order=0):
    """
    Register hook for ``hook_name``. Can be used as a decorator::

        @register('hook_name')
        def my_hook(...):
            pass

    or as a function call::

        def my_hook(...):
            pass
        register('hook_name', my_hook)
    """

    # Pretend to be a decorator if fn is not supplied
    if fn is None:

        def decorator(fn):
            register(hook_name, fn, order=order)
            return fn

        return decorator

    if isinstance(hook_name, (str,)):
        hook_names = [hook_name]
    elif isinstance(hook_name, (list, tuple, set)):
        hook_names = list(hook_name)
    else:
        raise ValueError(
            "hook_name '%s' for '%s' should be str, or list!" % (hook_name, fn.__name__)
        )

    for name in hook_names:
        if name not in _corehook:
            _corehook[name] = []
        _corehook[name].append((fn, order))


def search_for_corehook():
    global _searched_for_corehook
    if not _searched_for_corehook:
        list(get_app_submodules(configs.HOOK_FILE_NAME))
        _searched_for_corehook = True


def get_hooks(hook_name=None):
    """Return the hooks function sorted by their order."""
    search_for_corehook()
    if hook_name is None:
        return _corehook
    hooks = _corehook.get(hook_name, [])
    hooks = sorted(hooks, key=itemgetter(1))
    return [hook[0] for hook in hooks]
