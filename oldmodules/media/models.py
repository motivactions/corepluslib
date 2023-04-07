from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from easy_thumbnails.fields import ThumbnailerImageField

from coreplus.configs import coreplus_configs
from coreplus.settings.models import BaseSetting, register_setting

User = get_user_model()


@register_setting
class MediaSetting(BaseSetting):
    max_file_size = models.DecimalField(
        default=5.0,
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=False,
        help_text=_("Set maximum size for an uploaded file"),
        verbose_name=_("Max Image Size in Megabyte"),
    )
    image_extensions = models.TextField(
        null=True,
        blank=True,
        help_text=_("A comma-separated list of image extensions."),
        verbose_name=_("Accepted Image Extensions"),
    )
    video_extensions = models.TextField(
        null=True,
        blank=True,
        help_text=_("A comma-separated list of video extensions."),
        verbose_name=_("Accepted Video Extensions"),
    )
    audio_extensions = models.TextField(
        null=True,
        blank=True,
        help_text=_("A comma-separated list of audio extensions."),
        verbose_name=_("Accepted Audio Extensions"),
    )
    document_extensions = models.TextField(
        null=True,
        blank=True,
        help_text=_("A comma-separated list of document extensions."),
        verbose_name=_("Accepted Document Extensions"),
    )

    class Meta:
        verbose_name = _("Media Setting")
        verbose_name_plural = _("Media Settings")

    def check_field_value(self, field, default_exts):
        """
        Ensure that the inputted extensions are in the default extensions list
        """
        if field:
            exts = field.replace(" ", "").split(",")
            for ext in exts:
                if ext and ext not in default_exts:
                    raise ValidationError(
                        _("Extension %s is not in the default extensions list" % (ext))
                    )

    def save(self, *args, **kwargs):
        self.check_field_value(
            self.image_extensions, coreplus_configs.IMAGE_FILE_EXTENSIONS
        )
        self.check_field_value(
            self.audio_extensions, coreplus_configs.AUDIO_FILE_EXTENSIONS
        )
        self.check_field_value(
            self.video_extensions, coreplus_configs.VIDEO_FILE_EXTENSIONS
        )
        self.check_field_value(
            self.document_extensions, coreplus_configs.DOCUMENT_FILE_EXTENSIONS
        )
        return super().save()


class ImageGallery(models.Model):
    user = models.ForeignKey(
        User,
        related_name="galleries",
        on_delete=models.CASCADE,
        db_index=True,
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    image = ThumbnailerImageField(
        null=True,
        blank=False,
        upload_to="active_service_galleries",
        verbose_name=_("image"),
    )
    caption = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_("caption"),
        help_text=_("Image title."),
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("description"),
        help_text=_("Description."),
    )

    class Meta:
        unique_together = ("content_type", "object_id")
        verbose_name = _("Image Gallery")
        verbose_name_plural = _("Image Galleries")

    def __str__(self):
        return f"{self.content_object} Gallery"


class ImageGalleryModel(models.Model):

    galleries = GenericRelation(ImageGallery)

    class Meta:
        abstract = True
