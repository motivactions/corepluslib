from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.translation import gettext_lazy as _


class CorePlusNavigatorConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "coreplus.navigators"
    label = "coreplus_navigators"
    verbose_name = _("Navigators")

    def ready(self):
        post_migrate.connect(init_app, sender=self)
        return super().ready()


def init_app(sender, **kwargs):
    """Create initial main navigation menu"""
    from coreplus.navigators.models import Menu, Placeholder  # NOQA

    pass
