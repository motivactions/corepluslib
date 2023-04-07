from importlib import import_module

from django.urls import URLPattern, URLResolver, include
from django.utils.functional import cached_property


class DecoratedPatterns(object):
    """
    A wrapper for an urlconf that applies a decorator to all its views.
    """

    def __init__(self, urlconf_module, decorators):
        # ``urlconf_module`` may be:
        #   - an object with an ``urlpatterns`` attribute
        #   - an ``urlpatterns`` itself
        #   - the dotted Python path to a module with an ``urlpatters`` attribute
        self.urlconf = urlconf_module
        try:
            iter(decorators)
        except TypeError:
            decorators = [decorators]
        self.decorators = decorators

    def decorate_pattern(self, pattern):
        if isinstance(pattern, URLResolver):
            decorated = URLResolver(
                pattern.pattern,
                DecoratedPatterns(pattern.urlconf_module, self.decorators),
                pattern.default_kwargs,
                pattern.app_name,
                pattern.namespace,
            )
        else:
            callback = pattern.callback
            for decorator in reversed(self.decorators):
                callback = decorator(callback)
            decorated = URLPattern(
                pattern.pattern,
                callback,
                pattern.default_args,
                pattern.name,
            )
        return decorated

    @cached_property
    def urlpatterns(self):
        # urlconf_module might be a valid set of patterns, so we default to it.
        patterns = getattr(self.urlconf_module, "urlpatterns", self.urlconf_module)
        return [self.decorate_pattern(pattern) for pattern in patterns]

    @cached_property
    def urlconf_module(self):
        if isinstance(self.urlconf, str):
            return import_module(self.urlconf)
        else:
            return self.urlconf

    @cached_property
    def app_name(self):
        return getattr(self.urlconf_module, "app_name", None)


def decorator_include(decorators, arg, namespace=None):
    """
    A replacement for ``django.conf.urls.include`` that takes a decorator,
    or an iterable of view decorators as the first argument and applies them, in
    reverse order, to all views in the included urlconf.

    from django.contrib import admin
    from django.core.exceptions import PermissionDenied
    from django.urls import path
    from django.contrib.auth.decorators import login_required, user_passes_test

    from decorator_include import decorator_include

    from mysite.views import index

    def only_user(username):
        def check(user):
            if user.is_authenticated and user.username == username:
                return True
            raise PermissionDenied
        return user_passes_test(check)

    urlpatterns = [
        path('', views.index, name='index'),
        # will redirect to login page if not authenticated
        path('secret/', decorator_include(login_required, 'mysite.secret.urls')),
        # will redirect to login page if not authenticated
        # will return a 403 http error if the user does not have the "god" username
        path('admin/', decorator_include([login_required, only_user('god')], admin.site.urls),
    ]

    """
    if isinstance(arg, tuple) and len(arg) == 3 and not isinstance(arg[0], str):
        # Special case where the function is used for something like `admin.site.urls`, which
        # returns a tuple with the object containing the urls, the app name, and the namespace
        # `include` does not support this pattern (you pass directly `admin.site.urls`, without
        # using `include`) but we have to
        urlconf_module, app_name, namespace = arg
    else:
        urlconf_module, app_name, namespace = include(arg, namespace=namespace)
    return DecoratedPatterns(urlconf_module, decorators), app_name, namespace
