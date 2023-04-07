from django.template import Library
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from ..models import Placeholder

register = Library()


@register.simple_tag(takes_context=True)
def render_menu(context, menu_slug):
    request = context["request"]
    nav = Placeholder.objects.filter(slug=menu_slug).first()
    if nav:
        return nav.render_html(request, context={})
    else:
        message = _("Menu `%s` doesn't exist!" % menu_slug)
        return mark_safe(f"<div class='me-auto'>{message}</div>")
