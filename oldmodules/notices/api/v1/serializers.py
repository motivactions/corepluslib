from django.contrib.contenttypes.models import ContentType
from django.contrib.humanize.templatetags import humanize

from notifications.models import Notification
from rest_framework import serializers


class ContentTypeSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = ContentType
        fields = "__all__"

    def get_name(self, obj) -> str:
        return f"{obj.app_label}.{obj.model}"


class NotificationSerializer(serializers.ModelSerializer):
    actor_content_type = ContentTypeSerializer()
    target_content_type = ContentTypeSerializer()
    action_object_content_type = ContentTypeSerializer()
    data = serializers.DictField()
    target_object_id = serializers.IntegerField()
    actor_object_id = serializers.IntegerField()
    action_object_object_id = serializers.IntegerField()
    humanize_time = serializers.SerializerMethodField(required=False)

    class Meta:
        model = Notification
        fields = "__all__"

    def validate(self, attrs):
        # TODO: Add validation for data
        return super().validate(attrs)

    def get_humanize_time(self, obj):
        return humanize.naturaltime(obj.timestamp)
