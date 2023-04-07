from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MarkdownAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "coreplus.markdown"
    label = "coreplus_markdown"
    verbose_name = _("Markdown")
