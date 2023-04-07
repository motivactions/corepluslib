from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import models
from django.template.base import Template
from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import get_template, select_template
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from mptt.fields import TreeForeignKey
from mptt.managers import TreeManager
from mptt.models import MPTTModel
from mptt.utils import get_cached_trees


class PlaceholderManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("menu_root")


class MenuItemManager(TreeManager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).select_related("parent")


class Menu(MPTTModel):

    parent = TreeForeignKey(
        "self",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="children",
        help_text=_(
            "Menu Item can have a hierarchy. You might have a "
            "Music Item, and under that have children items for Jazz"
            " and Blues. Totally optional."
        ),
    )
    url = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    label = models.CharField(
        max_length=255,
        verbose_name=_("label"),
    )
    order = models.IntegerField(
        default=0,
    )
    icon = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text=_("Icon"),
    )
    slug = models.SlugField(
        unique=True,
        max_length=80,
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Description"),
    )
    classnames = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_("class names"),
    )
    groups = models.ManyToManyField(
        Group,
        verbose_name=_("groups"),
        blank=True,
        related_name="+",
        help_text=_(
            "The groups this menu belongs to. A menu will get all permissions"
            " granted to each of their groups."
        ),
    )

    @property
    def opts(self):
        return self._meta

    objects = MenuItemManager()
    icon = "menu"

    class Meta:
        verbose_name = _("Menu")
        verbose_name_plural = _("Menus")

    def __str__(self):
        return str(self.label)

    def has_perms(self, user=None):
        """Return True if user is superuser or in menu groups"""
        if user and getattr(user, "is_superuser", False):
            return True
        else:
            item_groups = {g.id for g in self.groups.all().values("id")}
            # Menu items not in groups
            if not bool(item_groups):
                return True
            user_groups = {g.id for g in user.groups.all().values("id")}
            permissions = user_groups.intersection(item_groups)
            return bool(permissions)

    def clean(self):
        if self.parent:
            parent = self.parent
            if self.parent == self:
                raise ValidationError("Parent category cannot be self.")
            if parent.parent and parent.parent == self:
                raise ValidationError("Cannot have circular Parents.")

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)


class Placeholder(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("name"))
    slug = models.SlugField(unique=True, max_length=80)
    menu_root = TreeForeignKey(
        Menu,
        blank=False,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    template_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_("template"),
    )
    template_string = models.TextField(null=True, blank=True)

    objects = PlaceholderManager()
    icon = "menu"

    class Meta:
        verbose_name = _("Placeholder")
        verbose_name_plural = _("Placeholders")

    def __str__(self):
        return str(self.name)

    @cached_property
    def template(self):
        return self.get_template()

    def full_clean(self, *args, **kwargs):
        if self.template_name:
            try:
                get_template(self.template_name)
            except TemplateDoesNotExist:
                raise ValidationError(
                    {"template": "%s does not exist." % self.template_name}
                )
            return super().full_clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)

    def get_menu_context(self, request, include_self=False):
        menus = self.menu_root.get_descendants(include_self=bool(include_self))
        roots = get_cached_trees(menus)
        menu_items = [node for node in roots if node.has_perms(request.user)]
        return {"menu_items": menu_items, "request": request}

    def get_template(self):
        """Return template name"""
        if not (self.template_string and self.template_name):
            default_templates = ["includes/%s.html" % self.slug, "menu.html"]
        if self.template_string:
            template = Template(template_string=self.template_string)
            return template
        template_name = (
            [self.template_name] if self.template_name else default_templates
        )
        return select_template(template_name)

    def render_html(self, request, context):
        context.update(self.get_menu_context(request))
        return self.template.render(context, request)
