from functools import update_wrapper
from inspect import isclass

from django.apps import apps
from django.contrib import messages
from django.contrib.admin import AdminSite as BaseAdminSite
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import NoReverseMatch, reverse
from django.utils.text import capfirst
from django.utils.translation import gettext as _
from django.views import View

from coreplus import hooks
from coreplus.configs import coreplus_configs


class AdminSite(BaseAdminSite):

    enable_nav_sidebar = True
    enable_app_index = True

    # Text to put at the end of each page's <title>.
    site_title = coreplus_configs.SITE_TITLE
    # Text to put in each page's <h1>.
    site_header = coreplus_configs.SITE_HEADER
    # Text to put at the top of the admin index page.
    index_title = coreplus_configs.INDEX_TITLE

    # Exclude app from app_list and prevent index
    app_excludes = coreplus_configs.APP_INDEX_EXCLUDES
    app_default_icons = coreplus_configs.DEFAULT_APP_ICONS

    app_index_template = coreplus_configs.APP_INDEX_TEMPLATE
    logout_template = coreplus_configs.LOGOUT_TEMPLATE

    def _build_app_dict(self, request, label=None):
        """
        Build the app dictionary. The optional `label` parameter filters models
        of a specific app.
        """
        app_dict = {}

        if label:
            models = {
                m: m_a
                for m, m_a in self._registry.items()
                if m._meta.app_label == label
            }
        else:
            models = self._registry

        for model, model_admin in models.items():
            app_label = model._meta.app_label
            app_config = apps.get_app_config(app_label)

            if app_label in self.app_excludes:
                continue

            # Check whether user has any perm for this module.
            # If so, add the module to the model_list.
            has_module_perms = model_admin.has_module_permission(request)
            if not has_module_perms:
                continue

            perms = model_admin.get_model_perms(request)
            if True not in perms.values():
                continue

            info = (app_label, model._meta.model_name)
            model_icon = getattr(model, "icon", None)
            if model_icon is None:
                if model._meta.model_name == "user":
                    model_icon = "account-circle-outline"
                else:
                    model_icon = "text-box-outline"

            model_dict = {
                "name": capfirst(model._meta.verbose_name_plural),
                "icon": model_icon,
                "object_name": model._meta.object_name,
                "perms": perms,
                "admin_url": None,
                "add_url": None,
            }
            if perms.get("change") or perms.get("view"):
                model_dict["view_only"] = not perms.get("change")
                try:
                    model_dict["admin_url"] = reverse(
                        "admin:%s_%s_changelist" % info, current_app=self.name
                    )
                except NoReverseMatch:
                    pass
            if perms.get("add"):
                try:
                    model_dict["add_url"] = reverse(
                        "admin:%s_%s_add" % info, current_app=self.name
                    )
                except NoReverseMatch:
                    pass

            if app_label in app_dict:
                app_dict[app_label]["models"].append(model_dict)
            else:
                icon = getattr(app_config, "icon", None)
                if icon is None:
                    icon = self.app_default_icons.get(app_label, "apps")
                app_dict[app_label] = {
                    "name": app_config.verbose_name,
                    "icon": icon,
                    "app_label": app_label,
                    "app_url": reverse(
                        "admin:app_list",
                        kwargs={"app_label": app_label},
                        current_app=self.name,
                    ),
                    "has_module_perms": has_module_perms,
                    "models": [model_dict],
                }

        if label:
            return app_dict.get(label)
        return app_dict

    def get_app_list(self, request):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        app_dict = self._build_app_dict(request)

        # Sort the apps alphabetically.
        app_list = sorted(app_dict.values(), key=lambda x: x["name"].lower())

        # Show app index base on app_config
        # Sort the models alphabetically within each app.
        valid_app_list = []
        for app in app_list:
            app_config = apps.get_app_config(app["app_label"])
            show_app_index = getattr(app_config, "show_app_index", True)
            if show_app_index:
                app["models"].sort(key=lambda x: x["name"])
                valid_app_list.append(app)
        return valid_app_list

    def each_context(self, request):
        context = super().each_context(request)
        context["is_app_index_enabled"] = self.enable_app_index
        # admin_menu = AdminMenu(attrs={"id": "adminMenu"})
        # context["admin_menu"] = admin_menu.render(context={"request": request})
        return context

    def app_index(self, request, app_label, extra_context=None):
        if not self.enable_app_index:
            messages.error(request, _("The app index page is disabled."))
            return redirect("admin:index")

        app_dict = self._build_app_dict(request, app_label)
        if not app_dict:
            messages.error(request, _("The requested admin page does not exist."))
            return redirect("admin:index")

        # Sort the models alphabetically within each app.
        app_dict["models"].sort(key=lambda x: x["name"])
        context = {
            **self.each_context(request),
            "title": _("%(app)s Administration") % {"app": app_dict["name"]},
            "subtitle": None,
            "app_list": [app_dict],
            "app_label": app_label,
            **(extra_context or {}),
        }
        template_names = [
            "admin/%s/app_index.html" % app_label,
            "admin/%s.html" % app_label,
            "admin/app_index.html",
        ]
        request.current_app = self.name
        return TemplateResponse(
            request,
            template_names,
            context,
        )

    def get_urls(self):
        # Since this module gets imported in the application's root package,
        # it cannot import models from other applications at the module level,
        # and django.contrib.contenttypes.views imports ContentType.
        from django.contrib.contenttypes import views as contenttype_views
        from django.urls import include, path, re_path

        def wrap(view, cacheable=False):
            def wrapper(*args, **kwargs):
                return self.admin_view(view, cacheable)(*args, **kwargs)

            wrapper.admin_site = self
            return update_wrapper(wrapper, view)

        # Get registered custom admin view
        funcs = hooks.get_hooks("REGISTER_ADMIN_VIEW")
        urlpatterns = []
        for func in funcs:
            url_path, view, name = func()
            if isclass(view):
                if not issubclass(view, View):
                    raise ImproperlyConfigured("%s must be subclass of View" % view)
                route = path(url_path, wrap(view.as_view()), name=name)
            else:
                route = path(url_path, wrap(view), name=name)
            urlpatterns.append(route)

        # Admin-site-wide views.
        urlpatterns += [
            path("", wrap(self.index), name="index"),
            path("login/", self.login, name="login"),
            path("logout/", wrap(self.logout), name="logout"),
            path(
                "password_change/",
                wrap(self.password_change, cacheable=True),
                name="password_change",
            ),
            path(
                "password_change/done/",
                wrap(self.password_change_done, cacheable=True),
                name="password_change_done",
            ),
            path("autocomplete/", wrap(self.autocomplete_view), name="autocomplete"),
            path("jsi18n/", wrap(self.i18n_javascript, cacheable=True), name="jsi18n"),
            path(
                "r/<int:content_type_id>/<path:object_id>/",
                wrap(contenttype_views.shortcut),
                name="view_on_site",
            ),
        ]

        # Add in each model's views, and create a list of valid URLS for the
        # app_index
        valid_app_labels = []
        for model, model_admin in self._registry.items():
            path_name = (model._meta.app_label, model._meta.model_name)

            # Attach model_admin to selected app_label
            # attach_to_app = getattr(model_admin, "attach_to_app", None)
            # if attach_to_app is not None:
            #     path_name = (attach_to_app, model._meta.model_name)

            urlpatterns += [
                path("%s/%s/" % path_name, include(model_admin.urls)),
            ]
            if model._meta.app_label not in valid_app_labels:
                valid_app_labels.append(model._meta.app_label)

        # If there were ModelAdmins registered, we should have a list of app
        # labels for which we need to allow access to the app_index view,

        if valid_app_labels:
            regex = r"^(?P<app_label>" + "|".join(valid_app_labels) + ")/$"
            urlpatterns += [
                re_path(regex, wrap(self.app_index), name="app_list"),
            ]

        if self.final_catch_all_view:
            urlpatterns.append(re_path(r"(?P<url>.*)$", wrap(self.catch_all_view)))

        return urlpatterns
