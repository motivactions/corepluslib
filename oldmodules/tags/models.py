from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from easy_thumbnails.fields import ThumbnailerImageField
from mptt.models import MPTTModel, TreeForeignKey
from taggit.models import ItemBase, TagBase

from coreplus.utils.slugs import unique_slugify

from .managers import TagManager


class Category(MPTTModel):

    order = models.IntegerField(
        default=0,
        help_text=_("Ordering number"),
    )
    parent = TreeForeignKey(
        "self",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="children",
        help_text=_(
            "Categories, unlike tags, can have a hierarchy. You might have a "
            "Jazz category, and under that have children categories for Bebop"
            " and Big Band. Totally optional."
        ),
    )
    icon = models.SlugField(
        null=True,
        blank=True,
        max_length=50,
        verbose_name=_("Icon"),
    )
    name = models.CharField(
        max_length=80,
        unique=True,
        verbose_name=_("Category Name"),
    )
    slug = models.SlugField(
        unique=True,
        null=True,
        blank=True,
        editable=False,
        max_length=80,
    )
    image = ThumbnailerImageField(
        null=True,
        blank=True,
        upload_to="icon_images",
        verbose_name=_("image"),
    )
    category_id = models.CharField(
        max_length=80,
        unique=True,
        verbose_name=_("Category ID"),
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["name"]
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        permissions = (
            ("import_category", _("Can import Category")),
            ("export_category", _("Can export Category")),
        )

    def __str__(self):
        return self.name

    @property
    def opts(self):
        return self.__class__._meta

    def clean(self):
        if self.parent:
            parent = self.parent
            if self.parent == self:
                raise ValidationError("Parent category cannot be self.")
            if parent.parent and parent.parent == self:
                raise ValidationError("Cannot have circular Parents.")

    def save(self, *args, **kwargs):
        if not self.slug:
            unique_slugify(self, self.name)
        return super().save(*args, **kwargs)


class Tag(TagBase):
    icon = models.SlugField(
        null=True,
        blank=True,
        max_length=50,
        verbose_name=_("Icon"),
    )
    image = ThumbnailerImageField(
        null=True,
        blank=True,
        upload_to="icon_images",
        verbose_name=_("image"),
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Description"),
    )
    created_at = models.DateTimeField(default=timezone.now)
    last_modified_at = models.DateTimeField(default=timezone.now)

    objects = TagManager()
    icon = "tag-outline"

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")

    @property
    def opts(self):
        return self._meta

    @property
    def title(self):
        return self.name

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)


class TaggedItemBase(ItemBase):
    tag = models.ForeignKey(
        Tag,
        related_name="%(app_label)s_%(class)s_items",
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True
