import logging

from django.apps import apps as django_apps
from django.conf import settings
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from drf_spectacular.utils import extend_schema
from filer.models import File, Folder
from rest_framework import status
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from .serializers import (
    FilerAudioVisualCreateSerializer,
    FilerAudioVisualSerializer,
    FilerFileCreateSerializer,
    FilerFileSerializer,
    FilerImageCreateSerializer,
    FilerImageSerializer,
)

logger = logging.getLogger(__name__)


class FilerImageViewSet(CreateModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = django_apps.get_model(settings.FILER_IMAGE_MODEL).objects.all()
    serializer_class = FilerImageSerializer

    @extend_schema(
        request=FilerImageCreateSerializer,
        responses=FilerImageSerializer,
    )
    def create(self, request, *args, **kwargs):
        """
        Upload image to file folder
        > To perform bulk create, input multiple 'file=(FILE)' parameters
        """
        res = []
        with transaction.atomic():
            for img in request.data.getlist("file", []):
                serializer = self.get_serializer(data={"file": img})
                serializer.is_valid(raise_exception=True)
                img = self.perform_create(serializer)
                res.append(img)
        return Response(res, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        folder = Folder.objects.get_or_create(name="images")[0]
        serializer.save(author=self.request.user, folder=folder)
        return serializer.data


class FilerAudioVisualViewSet(CreateModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = django_apps.get_model(settings.FILER_IMAGE_MODEL).objects.all()
    serializer_class = FilerAudioVisualSerializer

    def get_serializer_class(self):
        if self.action == "create":
            return FilerAudioVisualCreateSerializer
        return super().get_serializer_class()

    @extend_schema(
        request=FilerAudioVisualCreateSerializer,
        responses=FilerAudioVisualSerializer,
    )
    def create(self, request, *args, **kwargs):
        """
        Upload audio visual (audio, video, and image) to file folder
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.perform_create(serializer)

        resp_serializers = FilerAudioVisualSerializer(
            instance=obj, context=self.get_serializer_context()
        )
        headers = self.get_success_headers(serializer.data)
        return Response(
            resp_serializers.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):

        folder = Folder.objects.get_or_create(name="audio_visuals")[0]
        obj = serializer.save(author=self.request.user, folder=folder)
        logger.info(_("Audio Visual successfully uploaded"))
        return obj


class FilerFileViewSet(ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FilerFileSerializer

    def get_serializer_class(self):
        if self.action == "create":
            return FilerFileCreateSerializer
        return super().get_serializer_class()

    @extend_schema(
        request=FilerFileCreateSerializer,
        responses=FilerFileSerializer,
    )
    def create(self, request, *args, **kwargs):
        """
        Upload file (all types) to file folder
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.perform_create(serializer)

        resp_serializers = FilerFileSerializer(
            instance=obj, context=self.get_serializer_context()
        )
        headers = self.get_success_headers(serializer.data)
        return Response(
            resp_serializers.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        folder = Folder.objects.get_or_create(name="files")[0]
        obj = serializer.save(folder=folder)
        logger.info(_("File successfully uploaded"))
        return obj
