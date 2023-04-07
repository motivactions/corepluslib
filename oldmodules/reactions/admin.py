from django.contrib import admin

from .models import Bookmark, Flag, Reaction, Review


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ["user", "content_object"]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["user", "content_object", "target_object", "rating"]


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ["user", "content_object", "value"]
    list_filter = ["value"]


@admin.register(Flag)
class FlagAdmin(admin.ModelAdmin):
    list_display = ["user", "content_object", "value"]
    list_filter = ["value"]
