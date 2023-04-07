from django.contrib import messages
from django.contrib.sites.models import Site
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.text import capfirst
from django.utils.translation import gettext as _
from django.views.generic import FormView, View
from django.views.generic.base import ContextMixin

from .permissions import user_can_edit_setting_type
from .registries import registry


def get_model_from_url_params(app_name, model_name):
    """
    retrieve a content type from an app_name / model_name combo.
    Throw Http404 if not a valid setting type
    """
    model = registry.get_by_natural_key(app_name, model_name)
    if model is None:
        raise Http404
    return model


class EditCurrentSiteSetting(ContextMixin, View):
    edit_url_name = "settings_edit"

    def get(self, request, app_name, model_name, **kwargs):
        site_request = Site.objects.get_current(request)
        site = site_request or Site.objects.first()
        if not site:
            messages.error(
                request,
                _("This setting could not be opened because there is no site defined."),
            )
            return redirect("admin:index")
        return redirect(
            reverse(self.edit_url_name, args=(app_name, model_name, site.pk))
        )


class EditSetting(FormView):
    edit_url_name = "settings_edit"

    def dispatch(self, request, app_name, model_name, site_pk, *args, **kwargs):
        self.app_name = app_name
        self.model_name = model_name
        self.site_pk = site_pk
        self.model = get_model_from_url_params(app_name, model_name)

        if not user_can_edit_setting_type(request.user, self.model):
            messages.warning(
                request,
                _("You don't have permission to edit %s history.")
                % self.model._meta.verbose_name,
            )
            return redirect("admin:index")

        self.site = get_object_or_404(Site, pk=site_pk)
        self.setting_type_name = self.model._meta.verbose_name
        self.instance = self.model.for_site(self.site)
        self.form_class = self.model.get_form_class()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context["form"]
        context.update(
            {
                "title": self.model._meta.verbose_name_plural.title(),
                "opts": self.model._meta,
                "setting_type_name": self.setting_type_name,
                "instance": self.instance,
                "site": self.site,
                "media": form.media,
            }
        )
        return context

    def get_template_names(self):
        return [
            "admin/settings/%s.html" % self.model._meta.model_name,
            "admin/settings/edit.html",
        ]

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.instance
        return kwargs

    def form_valid(self, form):
        msg = _("%(setting_type)s updated.") % {
            "setting_type": capfirst(self.setting_type_name),
            "instance": self.instance,
        }
        form.save()
        messages.success(self.request, msg)
        return redirect(
            self.edit_url_name, self.app_name, self.model_name, self.site.pk
        )

    def form_invalid(self, form):
        messages.error(
            self.request, _("The setting could not be saved due to errors."), form
        )
        return super().form_invalid(form)
