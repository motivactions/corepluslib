import logging

from django.contrib.auth import get_user_model

from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ReadOnlyModelViewSet

from ...models import Category, Tag
from . import serializers

logger = logging.getLogger(__name__)

User = get_user_model()


class TagViewSet(ReadOnlyModelViewSet):
    authentication_classes = []
    permission_classes = []
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer
    filter_backends = [SearchFilter]
    search_fields = ["@name"]


class CategoryViewSet(ReadOnlyModelViewSet):
    authentication_classes = []
    permission_classes = []
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer
    filter_backends = [SearchFilter]
    search_fields = ["@name"]
