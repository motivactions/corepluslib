from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from filer.fields.file import FilerFileField

from coreplus import markdown
from coreplus.profanity.extras import ProfanityFilter
from coreplus.reactions.models import ReactionableModel
from coreplus.utils.models.models import StatusModel, TimeStampedModel

from .managers import DirectMessageManager

User = get_user_model()


class DirectMessage(ReactionableModel, TimeStampedModel, StatusModel):
    """
    Model for direct message
    """

    READ = "read"
    UNREAD = "unread"
    STATUS_CHOICES = (
        (READ, _("read")),
        (UNREAD, _("unread")),
    )

    sender = models.ForeignKey(
        User,
        related_name="sender_direct_messages",
        on_delete=models.CASCADE,
        db_index=True,
    )

    recipient = models.ForeignKey(
        User,
        related_name="recipient_direct_messages",
        on_delete=models.CASCADE,
        db_index=True,
    )

    content = models.TextField(
        null=True,
        blank=True,
        max_length=1000,
        verbose_name=_("Content"),
    )

    content_html = models.TextField(
        null=True,
        blank=True,
        editable=False,
        verbose_name=_("Content Html"),
    )

    objects = DirectMessageManager()

    class Meta:
        verbose_name = _("Direct Message")
        verbose_name_plural = _("Direct Messages")
        ordering = ("created",)

    def save(self, *args, **kwargs):
        """
        Set status to unread on create
        Apply profanity filter to content
        Parse content to content_html
        """
        if self._state.adding:
            self.status = self.UNREAD

        self.content = ProfanityFilter().censor(self.content)
        self.content_html = markdown.parse(self.content)
        return super().save(*args, **kwargs)


class DirectMessageAttachment(models.Model):
    """
    Model for direct message attachment
    """

    direct_message = models.ForeignKey(
        DirectMessage,
        related_name="attachments",
        on_delete=models.CASCADE,
    )

    attachment = FilerFileField(
        on_delete=models.CASCADE,
        related_name="direct_message_attachments",
    )

    class Meta:
        verbose_name = _("Direct Message Attachment")
        verbose_name_plural = _("Direct Message Attachments")
