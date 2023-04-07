from django.apps import apps
from django.urls.base import reverse

from coreplus import hooks

from .permissions import user_can_edit_setting_type


class Registry(list):
    def register(self, model, **kwargs):
        """
        Register a model as a setting, adding it to the admin menu
        """

        # Don't bother registering this if it is already registered
        if model in self:
            return model
        self.append(model)

        # Register a new menu item in the settings menu
        @hooks.register("REGISTER_SETTINGS_MENU_ITEM")
        def settings_menu_hook(request):
            has_perm = user_can_edit_setting_type(request.user, model)
            if has_perm:
                return {
                    "model": model,
                    "opts": model._meta,
                    "label": model._meta.verbose_name_plural.title(),
                    "url": reverse(
                        "settings_edit",
                        args=[model._meta.app_label, model._meta.model_name],
                    ),
                }
            else:
                return None

        # @hookup.register("REGISTER_SETTINGS_PERMISSION")
        # def permissions_hook():
        #     return Permission.objects.filter(
        #         content_type__app_label=model._meta.app_label,
        #         codename="change_{}".format(model._meta.model_name),
        #     )

        return model

    def register_decorator(self, model=None, **kwargs):
        """
        Register a model as a setting in the admin
        """
        if model is None:
            return lambda model: self.register(model, **kwargs)
        return self.register(model, **kwargs)

    def get_by_natural_key(self, app_label, model_name):
        """
        Get a setting model using its app_label and model_name.

        If the app_label.model_name combination is not a valid model, or the
        model is not registered as a setting, returns None.
        """
        try:
            Model = apps.get_model(app_label, model_name)
        except LookupError:
            return None
        if Model not in registry:
            return None
        return Model


registry = Registry()
register_setting = registry.register_decorator
