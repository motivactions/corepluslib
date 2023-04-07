from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.translation import gettext_lazy as _


class CorePlusHookConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "coreplus.media"
    label = "coreplus_media"
    verbose_name = _("Media")

    def ready(self):
        post_migrate.connect(init_app, sender=self)


def init_app(sender, **kwargs):
    pass
