from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin

from .models import Discuss


@admin.register(Discuss)
class DiscussAdmin(DraggableMPTTAdmin):
    list_display = list(DraggableMPTTAdmin.list_display) + ["reaction"]
