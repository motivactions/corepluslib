from django.urls import path

from .admin import admin_settings_edit, settings_edit_current_site, settings_view

urlpatterns = [
    path(
        "<str:app_name>/<str:model_name>/",
        settings_edit_current_site,
        name="settings_edit",
    ),
    path(
        "<str:app_name>/<str:model_name>/<int:site_pk>/",
        admin_settings_edit,
        name="settings_edit",
    ),
    path("", settings_view, name="settings"),
]
