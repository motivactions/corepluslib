from django.contrib import admin
from import_export.admin import ImportExportMixin
from taggit.models import Tag as TaggitTag

from . import models, resources


@admin.register(models.Category)
class CategoryAdmin(ImportExportMixin, admin.ModelAdmin):
    menu_icon = "tag"
    inspect_enabled = False
    list_display = ["name", "slug", "parent"]
    search_fields = ["name", "slug"]
    list_select_related = ["parent"]
    resource_class = resources.CategoryResource


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "description"]
    ordering = ["name", "slug"]
    search_fields = ["name", "description"]
    prepopulated_fields = {"slug": ["name"]}
