import logging

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from coreplus.utils.models.models import TimeStampedModel

from .managers import ShortUrlManager
from .utils import create_shortened_url

logger = logging.getLogger(__name__)

User = get_user_model()


class ShortUrl(TimeStampedModel):

    user = models.ForeignKey(
        User,
        related_name="short_urls",
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    url_shortened = models.CharField(
        max_length=15,
        unique=True,
        blank=True,
    )
    url_original = models.URLField()
    is_active = models.BooleanField(default=True)
    visitor = models.PositiveIntegerField(default=0)

    objects = ShortUrlManager()

    class Meta:
        ordering = ["-created"]
        verbose_name = _("Short URL")
        verbose_name_plural = _("Short URLs")

    def __str__(self):
        return f"{self.url_original} to {self.url_shortened}"

    def save(self, *args, **kwargs):
        # If the short url wasn't specified
        if not self.url_shortened:
            # We pass the model instance that is being saved
            self.url_shortened = create_shortened_url(self)
        super().save(*args, **kwargs)
