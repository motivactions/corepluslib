from django.contrib import admin
from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
from django.utils.translation import gettext_lazy as _

from .models import BaseSetting, GeneralSetting
from .views import EditCurrentSiteSetting, EditSetting


def admin_settings_edit(request, app_name, model_name, site_pk):
    context = {**admin.site.each_context(request)}
    return EditSetting.as_view(extra_context=context)(
        request, app_name, model_name, site_pk
    )


def settings_edit_current_site(request, app_name, model_name):
    context = {**admin.site.each_context(request)}
    return EditCurrentSiteSetting.as_view(extra_context=context)(
        request, app_name, model_name
    )


def settings_view(request, extra_context=None):
    general_settings = GeneralSetting
    if general_settings is None:
        raise Http404(_("General settings class not set!"))
    elif not issubclass(general_settings, (BaseSetting,)):
        raise ImproperlyConfigured(
            _(
                "General settings must be subclass of coreplus.settings.models.BaseSetting !"
            )
        )
    else:
        opts = general_settings._meta
        return settings_edit_current_site(request, opts.app_label, opts.model_name)
