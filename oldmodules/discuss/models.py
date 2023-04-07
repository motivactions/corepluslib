from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from mptt.models import MPTTModel, TreeForeignKey

from coreplus import markdown
from coreplus.profanity.extras import ProfanityFilter
from coreplus.reactions.models import FlaggableModel, ReactionableModel
from coreplus.utils.models.models import TimeStampedModel

User = get_user_model()


class DiscussManager(models.Manager):
    def __init__(self, *args, **kwargs):
        self.hide_blocked_user = kwargs.pop("hide_blocked_user", True)
        super().__init__(*args, **kwargs)

    def get_queryset(self):
        if self.hide_blocked_user:
            return super().get_queryset().filter(user__is_active=True)
        else:
            return super().get_queryset()

    def get(self, *args, **kwargs):
        if self.hide_blocked_user:
            kwargs["user__is_active"] = True
        return super().get(*args, **kwargs)


class Discuss(ReactionableModel, FlaggableModel, TimeStampedModel, MPTTModel):

    parent = TreeForeignKey(
        "self",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="children",
        help_text=_("Discuss can have a hierarchy, totally optional."),
    )

    user = models.ForeignKey(
        User,
        related_name="discuss",
        on_delete=models.CASCADE,
        db_index=True,
    )
    content_type = models.ForeignKey(
        ContentType,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        help_text=_("Parent comented content type."),
    )
    object_id = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text=_("Parent comented object id."),
    )
    content_object = GenericForeignKey()
    content = models.TextField(
        verbose_name=_("Content"),
    )
    content_html = models.TextField(
        editable=False,
        verbose_name=_("Content HTML"),
    )

    objects = DiscussManager()
    all_objects = DiscussManager(hide_blocked_user=False)

    class Meta:
        verbose_name = _("Discuss")
        verbose_name_plural = _("Discuss")

    def __str__(self):
        return f"{self.content_object} comment #{self.id}"

    @property
    def opts(self):
        return self.__class__._meta

    def clean(self):
        if self.parent:
            parent = self.parent
            if self.parent == self:
                raise ValidationError("Parent discuss cannot be self.")
            if parent.parent and parent.parent == self:
                raise ValidationError("Cannot have circular Parents.")

    def delete(self, descendants=True, *args, **kwargs):
        """Remove discuss objects include descendants"""
        if descendants:
            descendants = self.get_descendants(include_self=False)
            descendants.delete()
        return super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        """
        If parent is available then set parent behaviour to children
        Apply profanity filter to content
        Parse content to content_html
        """
        if self.parent:
            self.content_type = self.parent.content_type
            self.object_id = self.parent.object_id

        self.content = ProfanityFilter().censor(self.content)
        self.content_html = markdown.parse(self.content)
        return super().save(*args, **kwargs)
