from django.contrib import admin

from .models import DirectMessage, DirectMessageAttachment


class AttachmentInline(admin.StackedInline):
    model = DirectMessageAttachment
    extra = 0


@admin.register(DirectMessage)
class DirectMessageAdmin(admin.ModelAdmin):
    list_display = ["sender", "recipient", "status"]
    inlines = [AttachmentInline]
    readonly_fields = ["status"]


@admin.register(DirectMessageAttachment)
class DirectMessageAttachmentAdmin(admin.ModelAdmin):
    list_display = ["direct_message"]
