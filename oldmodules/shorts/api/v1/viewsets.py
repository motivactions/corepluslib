import logging

from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from ...models import ShortUrl
from .serializers import ShortUrlCreateSerializer, ShortUrlSerializer

logger = logging.getLogger(__name__)

User = get_user_model()


class ShortUrlViewSet(CreateModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = ShortUrl.objects.all()
    serializer_class = ShortUrlSerializer

    def get_serializer_class(self):
        if self.action == "create":
            return ShortUrlCreateSerializer
        return super().get_serializer_class()

    @extend_schema(
        request=ShortUrlCreateSerializer,
        responses=ShortUrlSerializer,
    )
    def create(self, request, *args, **kwargs):
        """Shorten long URL"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.perform_create(serializer)
        resp_serializer = ShortUrlSerializer(instance=obj)
        headers = self.get_success_headers(serializer.data)
        return Response(
            resp_serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        obj = serializer.save(user=self.request.user)
        return obj
