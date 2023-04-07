import logging

from rest_framework import serializers

from ...models import ShortUrl

logger = logging.getLogger(__name__)


class ShortUrlCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShortUrl
        fields = ["title", "description", "url_original"]


class ShortUrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShortUrl
        fields = "__all__"
