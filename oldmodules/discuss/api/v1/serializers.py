from django.contrib.humanize.templatetags import humanize

from rest_framework import serializers

from coreplus.configs import coreplus_configs
from coreplus.reactions.api.v1.serializers import ReactionableModelSerializer

from ...models import Discuss

UserSerializer = coreplus_configs.DEFAULT_USER_SERIALIZER


class DiscussSerializerRelation(serializers.ModelSerializer):
    user = UserSerializer(required=False)
    humanize_time = serializers.SerializerMethodField(required=False)

    class Meta:
        model = Discuss
        fields = "__all__"

    def get_humanize_time(self, obj):
        return humanize.naturaltime(obj.created)


class DiscussSerializer(ReactionableModelSerializer, serializers.ModelSerializer):
    parent = DiscussSerializerRelation(many=False)
    children = DiscussSerializerRelation(many=True)
    humanize_time = serializers.SerializerMethodField(required=False)
    user = UserSerializer(required=False)

    class Meta:
        model = Discuss
        fields = "__all__"

    def get_humanize_time(self, obj):
        return humanize.naturaltime(obj.created)


class DiscussCreateSerializer(serializers.ModelSerializer):
    """
    serializer to create a new discuss
    """

    class Meta:
        model = Discuss
        fields = ["content"]
