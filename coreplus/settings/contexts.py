from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.utils.functional import SimpleLazyObject

from .registries import registry


class SettingsProxy(dict):
    """
    Get a SettingModuleProxy for an app using proxy['app_label']
    """

    def __init__(self, request_or_site):
        self.request_or_site = request_or_site

    def __missing__(self, app_label):
        self[app_label] = value = SettingModuleProxy(self.request_or_site, app_label)
        return value

    def __str__(self):
        return "SettingsProxy"


class SettingModuleProxy(dict):
    """
    Get a setting instance using proxy['modelname']
    """

    def __init__(self, request_or_site, app_label):
        self.app_label = app_label
        self.request_or_site = request_or_site

    def __getitem__(self, model_name):
        """Get a setting instance for a model"""
        # Model names are treated as case-insensitive
        return super().__getitem__(model_name.lower())

    def __missing__(self, model_name):
        """Get and cache settings that have not been looked up yet"""
        self[model_name] = value = self.get_setting(model_name)
        return value

    def get_setting(self, model_name):
        """
        Get a setting instance
        """
        Model = registry.get_by_natural_key(self.app_label, model_name)
        if Model is None:
            return None

        if isinstance(self.request_or_site, Site):
            return Model.for_site(self.request_or_site)
        # Utilises cached value on request if set
        return Model.for_request(self.request_or_site)

    def __str__(self):
        return "SettingsModuleProxy({0})".format(self.app_label)


def settings(request):
    site = SimpleLazyObject(lambda: get_current_site(request))
    protocol = "https" if request.is_secure() else "http"

    # delay site query until settings values are needed
    def _inner(request):
        if site is None:
            # find_for_request() can't determine the site,
            # so no settings can be idenfified
            return {}
        else:
            return SettingsProxy(request)

    return {
        "site": site,
        "site_root": SimpleLazyObject(
            lambda: "{0}://{1}".format(protocol, site.domain)
        ),
        "settings": SimpleLazyObject(lambda: _inner(request)),
    }
