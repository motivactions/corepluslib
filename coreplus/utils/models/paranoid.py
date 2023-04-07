from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from polymorphic.models import PolymorphicManager


class ParanoidManagerMixin:
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

    def get(self, *args, **kwargs):
        kwargs["is_deleted"] = False
        return super().get(*args, **kwargs)

    def get_deleted(self):
        return super().get_queryset().filter(is_deleted=True)


class ParanoidManager(ParanoidManagerMixin, models.Manager):
    pass


class ParanoidPolymorphicManager(ParanoidManagerMixin, PolymorphicManager):
    pass


class ParanoidModel(models.Model):

    is_deleted = models.BooleanField(default=False, editable=False)
    deleted_at = models.DateTimeField(null=True, blank=True, editable=False)
    deletion_error_cautions = ""

    class Meta:
        abstract = True

    def pass_delete_validation(self, paranoid, user):
        return not self.is_deleted

    def get_deletion_error_message(self):
        msg = _("E1001: %s deletion can't be performed.")
        return msg % (self._meta.verbose_name, self.deletion_error_cautions)

    def get_deletion_message(self):
        msg = _("E1010: %s deleted succesfully.")
        return msg % self._meta.verbose_name

    def pass_restore_validation(self):
        return self.is_deleted

    def get_restoration_error_message(self):
        msg = _("E1002: %s restoration can't be performed.")
        return msg % self._meta.verbose_name

    def delete(self, using=None, keep_parents=False, paranoid=True, user=None):
        """
        Give paranoid delete mechanism to each record
        """
        if not self.pass_delete_validation(paranoid, user):
            raise ValidationError(self.get_deletion_error_message())

        if paranoid:
            self.is_deleted = True
            self.deleted_at = timezone.now()
            self.save()
        else:
            super().delete(using=using, keep_parents=keep_parents)

    def restore(self):
        if not self.pass_restore_validation():
            raise ValidationError(self.get_restoration_error_message())
        self.is_deleted = False
        self.deleted_at = None
        self.save()
