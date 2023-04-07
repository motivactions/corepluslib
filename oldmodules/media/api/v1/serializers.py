import logging

from django.apps import apps as django_apps
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from filer.models import File
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from coreplus.configs import coreplus_configs

from ...helpers import validate_file_type_api
from ...models import MediaSetting

logger = logging.getLogger(__name__)


class FilerBaseSerializer(serializers.ModelSerializer):
    """
    Base serializer for filer related serializers
    """

    def validate(self, attrs):
        """
        Ensure that the file is smaller than the max file size
        """
        media_settings = MediaSetting.for_request(self.context.get("request"))
        if attrs.get("file"):
            if attrs.get("file").size > media_settings.max_file_size * 1000000:
                raise ValidationError(
                    {
                        "file": "File size must be smaller than %s MB"
                        % (media_settings.max_file_size)
                    }
                )
        else:
            logger.error(_("File field is required"))
            raise ValidationError(_("File field is required"))
        return super().validate(attrs)


class FilerImageSerializer(FilerBaseSerializer):
    class Meta:
        model = django_apps.get_model(settings.FILER_IMAGE_MODEL, require_ready=False)
        fields = [
            "id",
            "file",
            "_file_size",
            "name",
            "description",
            "is_public",
            "author",
            "folder",
            "owner",
        ]

    def validate(self, attrs):
        """
        Ensure that the file is image
        """
        media_settings = MediaSetting.for_request(self.context.get("request"))
        if media_settings.image_extensions:
            exts = media_settings.image_extensions.replace(" ", "").split(",")
        else:
            exts = coreplus_configs.IMAGE_FILE_EXTENSIONS
        validate_file_type_api(attrs.get("file"), exts)
        return super().validate(attrs)


class FilerImageCreateSerializer(FilerBaseSerializer):
    class Meta:
        model = django_apps.get_model(settings.FILER_IMAGE_MODEL, require_ready=False)
        fields = ["file"]


class FilerFileSerializer(FilerBaseSerializer):
    class Meta:
        model = File
        fields = [
            "id",
            "file",
            "_file_size",
            "name",
            "description",
            "is_public",
            "folder",
            "owner",
        ]


class FilerFileCreateSerializer(FilerBaseSerializer):
    class Meta:
        model = File
        fields = ["file"]


class FilerAudioVisualSerializer(FilerBaseSerializer):
    class Meta:
        model = django_apps.get_model(settings.FILER_IMAGE_MODEL, require_ready=False)
        fields = "__all__"


class FilerAudioVisualCreateSerializer(FilerBaseSerializer):
    class Meta:
        model = django_apps.get_model(settings.FILER_IMAGE_MODEL, require_ready=False)
        fields = ["file"]

    def validate(self, attrs):
        """
        Ensure that the file is audio visual
        """
        media_settings = MediaSetting.for_request(self.context.get("request"))
        if media_settings.image_extensions:
            exts = media_settings.image_extensions.replace(" ", "").split(",")
        else:
            exts = coreplus_configs.IMAGE_FILE_EXTENSIONS
        if media_settings.audio_extensions:
            exts += media_settings.audio_extensions.replace(" ", "").split(",")
        else:
            exts += coreplus_configs.AUDIO_FILE_EXTENSIONS
        if media_settings.video_extensions:
            exts += media_settings.video_extensions.replace(" ", "").split(",")
        else:
            exts += coreplus_configs.VIDEO_FILE_EXTENSIONS
        validate_file_type_api(attrs.get("file"), exts)
        return super().validate(attrs)
