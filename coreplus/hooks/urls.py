from django.contrib import admin
from django.urls import path

from .admin import HookRegistryView

urlpatterns = [
    path(
        "",
        admin.site.admin_view(HookRegistryView.as_view()),
        name="hook_registry_view",
    )
]
