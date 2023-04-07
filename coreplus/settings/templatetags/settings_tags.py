from django.contrib.sites.models import Site
from django.template import Library, Node
from django.template.defaulttags import token_kwargs

from coreplus import hooks

from ..contexts import SettingsProxy

# from ..permissions import user_can_edit_setting_type

register = Library()


class GetSettingsNode(Node):
    def __init__(self, kwargs, target_var):
        self.kwargs = kwargs
        self.target_var = target_var

    @staticmethod
    def get_settings_object(context, use_default_site=True):
        if use_default_site:
            site = Site.objects.first()
            return SettingsProxy(site)
        if "request" in context:
            return SettingsProxy(context["request"])

        raise RuntimeError(
            "No request found in context, and use_default_site flag not set"
        )

    def render(self, context):
        resolved_kwargs = {k: v.resolve(context) for k, v in self.kwargs.items()}
        context[self.target_var] = self.get_settings_object(context, **resolved_kwargs)
        return ""


@register.tag
def get_settings(parser, token):
    bits = token.split_contents()[1:]
    target_var = "settings"
    if len(bits) >= 2 and bits[-2] == "as":
        target_var = bits[-1]
        bits = bits[:-2]
    kwargs = token_kwargs(bits, parser) if bits else {}
    return GetSettingsNode(kwargs, target_var)


@register.simple_tag(takes_context=True)
def get_settings_list(context, **kwargs):
    request = context["request"]
    funcs = hooks.get_hooks("REGISTER_SETTINGS_MENU_ITEM")
    menu_list = [func(request) for func in funcs if func(request) is not None]
    return menu_list
