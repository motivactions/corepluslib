from django.contrib.sites.models import Site
from django.db import models
from django.forms import modelform_factory
from django.utils.translation import gettext_lazy as _

from .registries import register_setting


class BaseSetting(models.Model):
    """
    The abstract base model for settings. Subclasses must be registered using
    :func:`coreplus.settings.models.registry.register_setting`
    """

    # Override to fetch ForeignKey values in the same query when
    # retrieving settings via for_site()
    select_related = None

    site = models.OneToOneField(
        Site,
        unique=True,
        db_index=True,
        editable=False,
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True

    @classmethod
    def base_queryset(cls):
        """
        Returns a queryset of objects of this type to use as a base
        for calling get_or_create() on.

        You can use the `select_related` attribute on your class to
        specify a list of foreign key field names, which the method
        will attempt to select additional related-object data for
        when the query is executed.

        If your needs are more complex than this, you can override
        this method on your custom class.
        """
        queryset = cls.objects.all()
        if cls.select_related is not None:
            queryset = queryset.select_related(*cls.select_related)
        return queryset

    @classmethod
    def for_site(cls, site):
        """
        Get or create an instance of this setting for the site.
        """
        queryset = cls.base_queryset()
        instance, created = queryset.get_or_create(site=site)
        return instance

    @classmethod
    def for_request(cls, request):
        """
        Get or create an instance of this model for the request,
        and cache the result on the request for faster repeat access.
        """
        attr_name = cls.get_cache_attr_name()
        if hasattr(request, attr_name):
            return getattr(request, attr_name)
        site = Site.objects.get_current(request=request)
        site_settings = cls.for_site(site)
        # to allow more efficient page url generation
        site_settings._request = request
        setattr(request, attr_name, site_settings)
        return site_settings

    @classmethod
    def get_cache_attr_name(cls):
        """
        Returns the name of the attribute that should be used to store
        a reference to the fetched/created object on a request.
        """
        return "_{}.{}".format(cls._meta.app_label, cls._meta.model_name).lower()

    @classmethod
    def get_form_class(cls):
        return modelform_factory(cls, fields="__all__")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return "%s for %s" % (self._meta.verbose_name.capitalize(), self.site)


@register_setting
class GeneralSetting(BaseSetting):
    site_logo = models.ImageField(
        null=True,
        blank=True,
        verbose_name=_("Logo"),
    )
    site_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_("Site Name"),
    )
    site_description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Site Name"),
    )

    class Meta:
        verbose_name = _("General Setting")
        verbose_name_plural = _("General Settings")
