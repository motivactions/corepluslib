from django.contrib import admin

from .models import Numerator


@admin.register(Numerator)
class NumeratorAdmin(admin.ModelAdmin):
    list_display = [
        "app_label",
        "model",
        "prefix",
        "reset_mode",
        "year",
        "month",
        "counter",
    ]
