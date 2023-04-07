from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin

from .models import Menu, Placeholder


@admin.register(Placeholder)
class PlaceholderModelAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "menu_root"]


@admin.register(Menu)
class MenuModelAdmin(DraggableMPTTAdmin):
    # list_display = ["menu_item", "parent"]
    pass
