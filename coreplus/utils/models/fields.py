import secrets
from collections.abc import Callable

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.db import models
from django.db.models.fields import CharField, DecimalField
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from .. import validators
from ..forms import fields as form_field_utils

DEFAULT_CHOICES_NAME = "STATUS_CHOICES"

SPLIT_MARKER = getattr(settings, "SPLIT_MARKER", "<!-- split -->")

# the number of paragraphs after which to split if no marker
SPLIT_DEFAULT_PARAGRAPHS = getattr(settings, "SPLIT_DEFAULT_PARAGRAPHS", 2)

# https://github.com/django/django/blob/64200c14e0072ba0ffef86da46b2ea82fd1e019a/
# django/db/models/fields/subclassing.py#L31-L44


class Creator(object):
    """
    A placeholder class that provides a way to set the attribute on the model.
    """

    def __init__(self, field):
        self.field = field

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        return obj.__dict__[self.field.name]

    def __set__(self, obj, value):
        obj.__dict__[self.field.name] = self.field.to_python(value)


class CustomGenericForeignKey(GenericForeignKey):
    def __init__(
        self,
        ct_field="content_type",
        fk_field="object_id",
        pk_field=None,
        *args,
        **kwargs
    ):
        self.pk_field = pk_field or "pk"
        super().__init__(ct_field, fk_field, *args, **kwargs)

    def __get__(self, instance, cls=None):
        if instance is None:
            return self

        # Don't use getattr(instance, self.ct_field) here because that might
        # reload the same ContentType over and over (#5570). Instead, get the
        # content type ID here, and later when the actual instance is needed,
        # use ContentType.objects.get_for_id(), which has a global cache.
        f = self.model._meta.get_field(self.ct_field)
        ct_id = getattr(instance, f.get_attname(), None)
        pk_val = getattr(instance, self.fk_field)

        rel_obj = self.get_cached_value(instance, default=None)
        if rel_obj is not None:
            ct_match = (
                ct_id == self.get_content_type(obj=rel_obj, using=instance._state.db).id
            )
            pk_match = getattr(rel_obj, self.pk_field, None) == rel_obj.pk
            if ct_match and pk_match:
                return rel_obj
            else:
                rel_obj = None
        if ct_id is not None:
            ct = self.get_content_type(id=ct_id, using=instance._state.db)
            try:
                filters = {self.pk_field: pk_val}
                rel_obj = ct.get_object_for_this_type(**filters)
            except ObjectDoesNotExist:
                pass
        self.set_cached_value(instance, rel_obj)
        return rel_obj

    def __set__(self, instance, value):
        ct = None
        fk = None
        # Get fk value by self.pk_field name
        if value is not None:
            ct = self.get_content_type(obj=value)
            fk = getattr(value, self.pk_field)

        setattr(instance, self.ct_field, ct)
        setattr(instance, self.fk_field, fk)
        self.set_cached_value(instance, value)


class AutoCreatedField(models.DateTimeField):
    """
    A DateTimeField that automatically populates itself at
    object creation.

    By default, sets editable=False, default=datetime.now.

    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("editable", False)
        kwargs.setdefault("default", now)
        super().__init__(*args, **kwargs)


class AutoLastModifiedField(AutoCreatedField):
    """
    A DateTimeField that updates itself on each save() of the model.

    By default, sets editable=False and default=datetime.now.

    """

    def get_default(self):
        """Return the default value for this field."""
        if not hasattr(self, "_default"):
            self._default = self._get_default()
        return self._default

    def pre_save(self, model_instance, add):
        value = now()
        if add:
            current_value = getattr(model_instance, self.attname, self.get_default())
            if current_value != self.get_default():
                # when creating an instance and the modified date is set
                # don't change the value, assume the developer wants that
                # control.
                value = getattr(model_instance, self.attname)
            else:
                for field in model_instance._meta.get_fields():
                    if isinstance(field, AutoCreatedField):
                        value = getattr(model_instance, field.name)
                        break
        setattr(model_instance, self.attname, value)
        return value


class StatusField(models.CharField):
    """
    A CharField that looks for a ``STATUS`` class-attribute and
    automatically uses that as ``choices``. The first option in
    ``STATUS`` is set as the default.

    Also has a default max_length so you don't have to worry about
    setting that.

    Also features a ``no_check_for_status`` argument to make sure
    South can handle this field when it freezes a model.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 100)
        self.check_for_status = not kwargs.pop("no_check_for_status", False)
        self.choices_name = kwargs.pop("choices_name", DEFAULT_CHOICES_NAME)
        super().__init__(*args, **kwargs)

    def prepare_class(self, sender, **kwargs):
        if not sender._meta.abstract and self.check_for_status:
            assert hasattr(sender, self.choices_name), (
                "To use StatusField, the model '%s' must have a %s choices class attribute."
                % (
                    sender.__name__,
                    self.choices_name,
                )
            )
            self.choices = getattr(sender, self.choices_name)
            if not self.has_default():
                self.default = tuple(getattr(sender, self.choices_name))[0][
                    0
                ]  # set first as default

    def contribute_to_class(self, cls, name):
        models.signals.class_prepared.connect(self.prepare_class, sender=cls)
        # we don't set the real choices until class_prepared (so we can rely on
        # the STATUS class attr being available), but we need to set some dummy
        # choices now so the super method will add the get_FOO_display method
        self.choices = [(0, "dummy")]
        super().contribute_to_class(cls, name)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["no_check_for_status"] = True
        return name, path, args, kwargs


class MonitorField(models.DateTimeField):
    """
    A DateTimeField that monitors another field on the same model and
    sets itself to the current date/time whenever the monitored field
    changes.

    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("default", now)
        monitor = kwargs.pop("monitor", None)
        if not monitor:
            raise TypeError(
                '%s requires a "monitor" argument' % self.__class__.__name__
            )
        self.monitor = monitor
        when = kwargs.pop("when", None)
        if when is not None:
            when = set(when)
        self.when = when
        super().__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name):
        self.monitor_attname = "_monitor_%s" % name
        models.signals.post_init.connect(self._save_initial, sender=cls)
        super().contribute_to_class(cls, name)

    def get_monitored_value(self, instance):
        return getattr(instance, self.monitor)

    def _save_initial(self, sender, instance, **kwargs):
        if self.monitor in instance.get_deferred_fields():
            # Fix related to issue #241 to avoid recursive error on double monitor fields
            return
        setattr(instance, self.monitor_attname, self.get_monitored_value(instance))

    def pre_save(self, model_instance, add):
        value = now()
        previous = getattr(model_instance, self.monitor_attname, None)
        current = self.get_monitored_value(model_instance)
        if previous != current:
            if self.when is None or current in self.when:
                setattr(model_instance, self.attname, value)
                self._save_initial(model_instance.__class__, model_instance)
        return super().pre_save(model_instance, add)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["monitor"] = self.monitor
        if self.when is not None:
            kwargs["when"] = self.when
        return name, path, args, kwargs


def _excerpt_field_name(name):
    return "_%s_excerpt" % name


def get_excerpt(content):
    excerpt = []
    default_excerpt = []
    paras_seen = 0
    for line in content.splitlines():
        if not line.strip():
            paras_seen += 1
        if paras_seen < SPLIT_DEFAULT_PARAGRAPHS:
            default_excerpt.append(line)
        if line.strip() == SPLIT_MARKER:
            return "\n".join(excerpt)
        excerpt.append(line)

    return "\n".join(default_excerpt)


class SplitText:
    def __init__(self, instance, field_name, excerpt_field_name):
        # instead of storing actual values store a reference to the instance
        # along with field names, this makes assignment possible
        self.instance = instance
        self.field_name = field_name
        self.excerpt_field_name = excerpt_field_name

    # content is read/write
    @property
    def content(self):
        return self.instance.__dict__[self.field_name]

    @content.setter
    def content(self, val):
        setattr(self.instance, self.field_name, val)

    # excerpt is a read only property
    def _get_excerpt(self):
        return getattr(self.instance, self.excerpt_field_name)

    excerpt = property(_get_excerpt)

    # has_more is a boolean property
    def _get_has_more(self):
        return self.excerpt.strip() != self.content.strip()

    has_more = property(_get_has_more)

    def __str__(self):
        return self.content


class SplitDescriptor:
    def __init__(self, field):
        self.field = field
        self.excerpt_field_name = _excerpt_field_name(self.field.name)

    def __get__(self, instance, owner):
        if instance is None:
            raise AttributeError("Can only be accessed via an instance.")
        content = instance.__dict__[self.field.name]
        if content is None:
            return None
        return SplitText(instance, self.field.name, self.excerpt_field_name)

    def __set__(self, obj, value):
        if isinstance(value, SplitText):
            obj.__dict__[self.field.name] = value.content
            setattr(obj, self.excerpt_field_name, value.excerpt)
        else:
            obj.__dict__[self.field.name] = value


class SplitField(models.TextField):
    def __init__(self, *args, **kwargs):
        # for South FakeORM compatibility: the frozen version of a
        # SplitField can't try to add an _excerpt field, because the
        # _excerpt field itself is frozen as well. See introspection
        # rules below.
        self.add_excerpt_field = not kwargs.pop("no_excerpt_field", False)
        super().__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name):
        if self.add_excerpt_field and not cls._meta.abstract:
            excerpt_field = models.TextField(editable=False)
            cls.add_to_class(_excerpt_field_name(name), excerpt_field)
        super().contribute_to_class(cls, name)
        setattr(cls, self.name, SplitDescriptor(self))

    def pre_save(self, model_instance, add):
        value = super().pre_save(model_instance, add)
        excerpt = get_excerpt(value.content)
        setattr(model_instance, _excerpt_field_name(self.attname), excerpt)
        return value.content

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return value.content

    def get_prep_value(self, value):
        try:
            return value.content
        except AttributeError:
            return value

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["no_excerpt_field"] = True
        return name, path, args, kwargs


class UrlsafeTokenField(models.CharField):
    """
    A field for storing a unique token in database.
    """

    def __init__(self, editable=False, max_length=128, factory=None, **kwargs):
        """
        Parameters
        ----------
        editable: bool
            If true token is editable.
        max_length: int
            Maximum length of the token.
        factory: callable
            If provided, called with max_length of the field instance to generate token.

        Raises
        ------
        TypeError
            non-callable value for factory is not supported.
        """

        if factory is not None and not isinstance(factory, Callable):
            raise TypeError("'factory' should either be a callable not 'None'")
        self._factory = factory

        kwargs.pop("default", None)  # passing default value has not effect.

        super().__init__(editable=editable, max_length=max_length, **kwargs)

    def get_default(self):
        if self._factory is not None:
            return self._factory(self.max_length)
        # generate a token of length x1.33 approx. trim up to max length
        token = secrets.token_urlsafe(self.max_length)[: self.max_length]
        return token

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["factory"] = self._factory
        return name, path, args, kwargs


class ExtendedURLField(CharField):
    description = _("URL")

    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = kwargs.get("max_length", 200)
        CharField.__init__(self, *args, **kwargs)
        self.validators.append(validators.ExtendedURLValidator())

    def formfield(self, **kwargs):
        """
        As with CharField, this will cause URL validation to be performed
        twice.
        """
        defaults = {
            "form_class": form_field_utils.ExtendedURLField,
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)

    def deconstruct(self):
        """
        deconstruct() is needed by Django's migration framework
        """
        name, path, args, kwargs = super().deconstruct()
        # We have a default value for max_length; remove it in that case
        if self.max_length == 200:
            del kwargs["max_length"]
        return name, path, args, kwargs


class PositiveDecimalField(DecimalField):
    """
    A simple subclass of ``django.db.models.fields.DecimalField`` that
    restricts values to be non-negative.
    """

    def formfield(self, **kwargs):
        """
        Return a :py:class:`django.forms.Field` instantiated with a ``min_value`` of 0.
        """
        return super().formfield(min_value=0)


class UppercaseCharField(CharField):
    """
    A simple subclass of ``django.db.models.fields.CharField`` that
    restricts all text to be uppercase.
    """

    def contribute_to_class(self, cls, name, **kwargs):
        super().contribute_to_class(cls, name, **kwargs)
        setattr(cls, self.name, Creator(self))

    def from_db_value(self, value, *args, **kwargs):
        return self.to_python(value)

    def to_python(self, value):
        """
        Cast the supplied value to uppercase
        """
        val = super().to_python(value)
        if isinstance(val, str):
            return val.upper()
        else:
            return val


class NullCharField(CharField):
    """
    CharField that stores '' as None and returns None as ''
    Useful when using unique=True and forms. Implies null==blank==True.

    Django's CharField stores '' as None, but does not return None as ''.
    """

    description = "CharField that stores '' as None and returns None as ''"

    def __init__(self, *args, **kwargs):
        if not kwargs.get("null", True) or not kwargs.get("blank", True):
            raise ImproperlyConfigured("NullCharField implies null==blank==True")
        kwargs["null"] = kwargs["blank"] = True
        super().__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name, **kwargs):
        super().contribute_to_class(cls, name, **kwargs)
        setattr(cls, self.name, Creator(self))

    def from_db_value(self, value, *args, **kwargs):
        value = self.to_python(value)
        # If the value was stored as null, return empty string instead
        return value if value is not None else ""

    def get_prep_value(self, value):
        prepped = super().get_prep_value(value)
        return prepped if prepped != "" else None

    def deconstruct(self):
        """
        deconstruct() is needed by Django's migration framework
        """
        name, path, args, kwargs = super().deconstruct()
        del kwargs["null"]
        del kwargs["blank"]
        return name, path, args, kwargs