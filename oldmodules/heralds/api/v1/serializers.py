from django.apps import apps as django_apps
from django.conf import settings
from django.contrib.humanize.templatetags import humanize

from rest_framework import serializers

from coreplus.configs import coreplus_configs
from coreplus.reactions.api.v1.serializers import ReactionableModelSerializer

from ...models import DirectMessage, DirectMessageAttachment

UserSerializer = coreplus_configs.DEFAULT_USER_SERIALIZER


class FilerImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = django_apps.get_model(settings.FILER_IMAGE_MODEL, require_ready=False)
        fields = ["id", "file", "name", "_height", "_width"]


class AttachmentSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    file = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    height = serializers.SerializerMethodField()
    width = serializers.SerializerMethodField()

    class Meta:
        model = DirectMessageAttachment
        fields = ["id", "file", "name", "height", "width"]

    def get_id(self, obj):
        return obj.attachment.id

    def get_file(self, obj):
        return obj.attachment.file.url

    def get_name(self, obj):
        return obj.attachment.name

    def get_height(self, obj):
        return obj.attachment._height

    def get_width(self, obj):
        return obj.attachment._width


class DirectMessageSerializer(ReactionableModelSerializer, serializers.ModelSerializer):
    sender = UserSerializer(required=False)
    recipient = UserSerializer(required=False)
    attachments = AttachmentSerializer(many=True, read_only=True)
    humanize_time = serializers.SerializerMethodField(required=False)

    class Meta:
        model = DirectMessage
        fields = "__all__"

    def get_humanize_time(self, obj):
        return humanize.naturaltime(obj.created)


class DirectMessageCreateSerializer(serializers.ModelSerializer):
    attachment_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )

    class Meta:
        model = DirectMessage
        fields = ["content", "recipient", "attachment_ids"]
