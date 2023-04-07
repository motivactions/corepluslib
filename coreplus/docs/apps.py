from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CorePlusDocsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "coreplus.docs"
    label = "coreplus_docs"
    verbose_name = _("Docs")
