from django.contrib import admin, messages
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.contrib.auth import get_permission_codename
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, TemplateView

from coreplus.configs import coreplus_configs


class AdminView(TemplateView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def has_permission(self, request=None, obj=None):
        return True

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(admin.site.each_context(self.request))
        return context

    def has_action_permission(self, request, action):
        opts = self.opts
        codename = get_permission_codename(action, opts)
        return request.user.has_perm("%s.%s" % (opts.app_label, codename))


class AdminFormView(FormView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def has_action_permission(self, request, action):
        opts = self.opts
        codename = get_permission_codename(action, opts)
        return request.user.has_perm("%s.%s" % (opts.app_label, codename))

    def has_permission(self, request=None, obj=None):
        return True

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(admin.site.each_context(self.request))
        return context


class BaseModelAdmin(admin.ModelAdmin):

    confirmation_template = "admin/confirmation.html"

    def has_action_permission(self, request, action):
        opts = self.opts
        codename = get_permission_codename(action, opts)
        return request.user.has_perm("%s.%s" % (opts.app_label, codename))

    def get_changelist_url(self):
        return reverse(admin_urlname(self.opts, "changelist"))

    def get_add_url(self):
        return reverse(admin_urlname(self.opts, "add"))

    def get_change_url(self, object_id):
        return reverse(admin_urlname(self.opts, "change"), args=(object_id,))

    def get_delete_url(self, object_id):
        return reverse(admin_urlname(self.opts, "delete"), args=(object_id,))

    def get_history_url(self, object_id):
        return reverse(admin_urlname(self.opts, "history"), args=(object_id,))

    def get_object_buttons_childs(self, request, obj):
        childs = []
        return childs

    def get_object_buttons_template(self, request, obj):
        return "admin/object_buttons.html"

    @admin.display(description="")
    def object_buttons(self, obj):
        childs = self.get_object_buttons_childs(self.request, obj)
        template = self.get_object_buttons_template(self.request, obj)
        context = {"request": self.request, "childs": childs, "object": obj}
        return render_to_string(template, context)

    def changelist_view(self, request, extra_context=None):
        self.request = request
        return super().changelist_view(request, extra_context)

    def confirmation_view(self, request, extra_context={}):
        context = {
            "request": request,
            "opts": self.opts,
            **self.admin_site.each_context(request),
            **extra_context,
        }
        return TemplateResponse(
            request,
            self.confirmation_template,
            context=context,
        )


class AdminPrintViewMixin(BaseModelAdmin):
    print_options = coreplus_configs.PRINT_OPTIONS
    print_filename = None
    print_template = None
    header_template = None
    footer_template = None
    cover_template = None
    print_view_class = coreplus_configs.PRINT_VIEW_CLASS

    def get_print_template(self):
        return self.print_template or [
            "admin/%s/%s/print.html" % (self.opts.app_label, self.opts.model_name),
            "admin/%s/%s_print.html" % (self.opts.app_label, self.opts.model_name),
            "admin/%s_%s_print.html" % (self.opts.app_label, self.opts.model_name),
            "admin/%s_print.html" % (self.opts.model_name),
            "admin/print.html",
        ]

    def get_print_filename(self):
        return self.print_filename or "%s_print.pdf" % self.opts.model_name

    def get_print_options(self):
        return self.print_options

    def get_cover_template(self):
        return self.cover_template

    def get_header_template(self):
        return self.header_template

    def get_footer_template(self):
        return self.footer_template

    def get_print_context(self, **kwargs):
        kwargs.update({"opts": self.opts})
        return kwargs

    def get_print_view_class(self):
        return self.print_view_class

    def get_print_url(self, object_id):
        return reverse(admin_urlname(self.opts, "print"), args=(object_id,))

    def has_print_permission(self, request, obj=None):
        return self.has_view_permission(request)

    def print_view(self, request, pk, *args, **kwargs):
        self.request = request
        obj = get_object_or_404(self.model, pk=pk)

        self.object = obj

        if not self.has_print_permission(request, obj):
            messages.error(request, _("You don't have permission to print this object"))
            try:
                return redirect(self.get_inspect_url(object_id=obj.id))
            except Exception:
                return redirect(self.get_change_url(object_id=obj.id))

        init_kwargs = dict(
            cmd_options=self.get_print_options(),
            filename=self.get_print_filename(),
            template_name=self.get_print_template(),
            cover_template=self.get_cover_template(),
            header_template=self.get_header_template(),
            footer_template=self.get_footer_template(),
            extra_context=self.get_print_context(object=obj, request=request),
        )
        view_class = self.get_print_view_class()
        return view_class.as_view(**init_kwargs)(request, pk, *args, **kwargs)

    def get_urls(self):
        super_urls = super().get_urls()
        urls = [
            path(
                "<int:pk>/print/",
                self.print_view,
                name="%s_%s_print" % (self.opts.app_label, self.opts.model_name),
            ),
        ]
        urls += super_urls
        return urls


class AdminInspectionMixin(BaseModelAdmin):
    inspect_enabled = True
    inspect_template = None
    inspect_title = None

    def get_inspect_url(self, object_id):
        return reverse(admin_urlname(self.opts, "inspect"), args=(object_id,))

    def get_object_buttons_childs(self, request, obj):
        childs = super().get_object_buttons_childs(request, obj)
        if self.inspect_enabled:
            childs += [
                {
                    "url": reverse(admin_urlname(self.opts, "inspect"), args=(obj.id,)),
                    "classes": "btn btn-sm btn-primary",
                    "label": _("Inspect"),
                }
            ]
        return childs

    def get_inspect_title(self, obj):
        return self.inspect_title or _("Inspecting %s") % obj

    def get_inspect_context(self, **kwargs):
        kwargs.update(
            {
                "opts": self.opts,
                "object": self.object,
                "title": self.get_inspect_title(self.object),
                "available_apps": admin.site.get_app_list(self.request),
                "has_change_permission": self.has_change_permission(
                    self.request, self.object
                ),
                "has_add_permission": self.has_add_permission(self.request),
                "has_delete_permission": self.has_delete_permission(
                    self.request, self.object
                ),
                "has_view_permission": self.has_view_permission(
                    self.request, self.object
                ),
                **self.admin_site.each_context(self.request),
            }
        )
        has_print_permission = getattr(self, "has_print_permission", None)
        if has_print_permission:
            kwargs["has_print_permission"] = has_print_permission(
                self.request, self.object
            )
        return kwargs

    def get_inspect_template(self):
        return self.inspect_template or [
            "admin/%s/%s/inspect.html" % (self.opts.app_label, self.opts.model_name),
            "admin/%s/%s_inspect.html" % (self.opts.app_label, self.opts.model_name),
            "admin/%s_%s_inspect.html" % (self.opts.app_label, self.opts.model_name),
            "admin/%s_inspect.html" % (self.opts.model_name),
            "admin/inspect.html",
        ]

    def inspect_view(self, request, pk, **kwargs):
        self.request = request
        self.object_id = pk
        self.object = get_object_or_404(self.model, pk=pk)
        return TemplateResponse(
            request=request,
            template=self.get_inspect_template(),
            context=self.get_inspect_context(**kwargs),
        )

    def change_view(self, request, object_id, form_url="", extra_context=None):
        if object_id not in [None, "", "None"]:
            try:
                obj = get_object_or_404(self.model, pk=object_id)
                if self.inspect_enabled and not self.has_change_permission(
                    request, obj
                ):
                    return redirect(self.get_inspect_url(object_id))
            except Exception:
                pass
        return super().change_view(
            request, object_id, form_url=form_url, extra_context=extra_context
        )

    def get_urls(self):
        super_urls = super().get_urls()
        urls = []
        if self.inspect_enabled:
            urls.append(
                path(
                    "<int:pk>/inspect/",
                    self.admin_site.admin_view(self.inspect_view),
                    name="%s_%s_inspect" % (self.opts.app_label, self.opts.model_name),
                ),
            )
        urls += super_urls
        return urls


class AdminReadOnlyMixin(BaseModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ModelAdminMixin(AdminInspectionMixin):
    pass


class ModelAdmin(BaseModelAdmin):
    pass
