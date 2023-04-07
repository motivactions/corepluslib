from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.translation import gettext_lazy as _


class CorePlusShortsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "coreplus.shorts"
    label = "coreplus_shorts"
    verbose_name = _("Shorts")

    def ready(self):
        post_migrate.connect(init_app, sender=self)
        return super().ready()


def init_app(sender, **kwargs):
    """For initializations"""
    pass
