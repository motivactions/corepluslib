from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from . import signals


class ActionMixin(models.Model):
    status = NotImplementedError

    class Meta:
        abstract = True

    @property
    def is_editable(self):
        """Check order is editable"""
        return self.is_trash or self.is_draft

    @property
    def opts(self):
        return self.__class__._meta


class TrashAction(ActionMixin, models.Model):

    date_trashed = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
        verbose_name=_("date trashed"),
    )

    class Meta:
        abstract = True

    @property
    def is_trash(self):
        """Check order status is trashed"""
        return self.status == self.TRASH

    def trash(self, request=None):
        return self._trash(request)

    @transaction.atomic
    def _trash(self, request=None):
        self.allow_trash
        signals.pre_trash.send(
            sender=self.__class__,
            instance=self,
            actor=request.user,
            request=request,
        )
        self.status = self.TRASH
        self.date_trashed = timezone.now()
        self.save()
        signals.post_trash.send(
            sender=self.__class__,
            instance=self,
            actor=request.user,
            request=request,
        )


class DraftAction(ActionMixin, models.Model):

    date_drafted = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
        verbose_name=_("date drafted"),
    )

    class Meta:
        abstract = True

    @property
    def is_draft(self):
        """Check order status is draft"""
        return self.status == self.DRAFT

    def draft(self, request=None):
        return self._draft(request)

    @transaction.atomic
    def _draft(self, request=None):
        """Draft trashed"""
        signals.pre_draft.send(
            sender=self.__class__,
            instance=self,
            actor=request.user,
            request=request,
        )
        self.status = self.DRAFT
        self.date_drafted = timezone.now()
        self.save()
        signals.post_draft.send(
            sender=self.__class__,
            instance=self,
            actor=request.user,
            request=request,
        )


class PendingAction(ActionMixin, models.Model):

    date_pending = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
        verbose_name=_("date pending"),
    )

    class Meta:
        abstract = True

    @property
    def is_pending(self):
        """Check order status is pending"""
        return self.status == self.PENDING

    def pending(self, request=None):
        return self._pending(request)

    @transaction.atomic
    def _pending(self, request=None):
        """pending trashed"""
        if self.is_pending:
            return
        if self.is_trash:
            self.status = self.PENDING
            self.date_pending = timezone.now()
            self.save()
        else:
            raise PermissionError(self.get_error_msg("pending"))


class ValidateAction(ActionMixin, models.Model):

    date_validated = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
        verbose_name=_("date validated"),
    )

    class Meta:
        abstract = True

    @property
    def is_valid(self):
        """Check order status is valid"""
        return self.status == self.VALID

    def validate(self, request=None):
        return self._validate(request)

    @transaction.atomic
    def _validate(self, request=None):
        """Validate drafted order"""
        signals.pre_validate.send(
            sender=self.__class__,
            instance=self,
            actor=request.user,
            request=request,
        )
        self.status = self.VALID
        self.date_validated = timezone.now()
        self.save()
        signals.post_validate.send(
            sender=self.__class__,
            instance=self,
            actor=request.user,
            request=request,
        )


class CancelAction(ActionMixin, models.Model):

    date_canceled = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
        verbose_name=_("date canceled"),
    )

    class Meta:
        abstract = True

    @property
    def is_canceled(self):
        """Check order status is canceled"""
        return self.status == self.CANCELED

    def cancel(self, request=None):
        return self._cancel(request)

    @transaction.atomic
    def _cancel(self, request=None):
        signals.pre_cancel.send(
            sender=self.__class__,
            instance=self,
            actor=request.user,
            request=request,
        )
        self.status = self.CANCELED
        self.date_canceled = timezone.now()
        self.save()
        signals.post_cancel.send(
            sender=self.__class__,
            instance=self,
            actor=request.user,
            request=request,
        )


class ApproveAction(ActionMixin, models.Model):

    date_approved = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
        verbose_name=_("date approved"),
    )

    class Meta:
        abstract = True

    @property
    def is_approved(self):
        """Check order status is approved"""
        return self.status == self.APPROVED

    def approve(self, request=None):
        return self._approve(request)

    @transaction.atomic
    def _approve(self, request=None):
        signals.pre_approve.send(
            sender=self.__class__,
            instance=self,
            actor=request.user,
            request=request,
        )
        self.status = self.APPROVED
        self.date_approved = timezone.now()
        self.save()
        signals.post_approve.send(
            sender=self.__class__,
            instance=self,
            actor=request.user,
            request=request,
        )


class RejectAction(ActionMixin, models.Model):

    date_rejected = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
        verbose_name=_("date rejected"),
    )

    class Meta:
        abstract = True

    @property
    def is_rejected(self):
        """Check order status is rejected"""
        return self.status == self.REJECTED

    def reject(self, request=None):
        return self._reject(request)

    @transaction.atomic
    def _reject(self, request=None):
        """Reject valid order"""
        signals.post_reject.send(
            sender=self.__class__,
            instance=self,
            actor=request.user,
            request=request,
        )
        self.status = self.REJECTED
        self.date_rejected = timezone.now()
        self.save()
        signals.post_reject.send(
            sender=self.__class__,
            instance=self,
            actor=request.user,
            request=request,
        )


class CompleteAction(ActionMixin, models.Model):

    date_completed = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
        verbose_name=_("date completed"),
    )

    class Meta:
        abstract = True

    @property
    def is_complete(self):
        """Check order status is complete"""
        return self.status == self.COMPLETE

    def complete(self, request=None):
        return self._complete(request)

    @transaction.atomic
    def _complete(self, request=None):
        """Complete validated order"""
        signals.pre_complete.send(
            sender=self.__class__,
            instance=self,
            actor=request.user,
            request=request,
        )
        self.status = self.COMPLETE
        self.date_completed = timezone.now()
        self.save()
        signals.post_complete.send(
            sender=self.__class__,
            instance=self,
            actor=request.user,
            request=request,
        )


class ProcessAction(ActionMixin, models.Model):

    date_processed = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
        verbose_name=_("date processed"),
    )

    class Meta:
        abstract = True

    @property
    def is_processed(self):
        """Check order status is processed"""
        return self.status == self.PROCESSED

    def process(self, request=None):
        return self._process(request)

    @transaction.atomic
    def _process(self, request=None):
        """Process valid order"""
        signals.pre_process.send(
            sender=self.__class__,
            instance=self,
            actor=request.user,
            request=request,
        )
        self.status = self.PROCESSED
        self.date_processed = timezone.now()
        self.save()
        signals.post_process.send(
            sender=self.__class__,
            instance=self,
            actor=request.user,
            request=request,
        )


class PaidAction(ActionMixin, models.Model):

    date_paid = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
        verbose_name=_("date paid"),
    )

    class Meta:
        abstract = True

    @property
    def is_paid(self):
        return self.status == self.REJECTED

    def pay(self, request=None):
        return self._pay(request)

    @transaction.atomic
    def _pay(self, request=None):
        """Paid pending order"""
        signals.pre_pay.send(
            sender=self.__class__,
            instance=self,
            actor=request.user,
            request=request,
        )
        self.status = self.PAID
        self.date_paid = timezone.now()
        self.save()
        signals.post_pay.send(
            sender=self.__class__,
            instance=self,
            actor=request.user,
            request=request,
        )


class CloseAction(ActionMixin, models.Model):

    date_closed = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
        verbose_name=_("date closed"),
    )

    class Meta:
        abstract = True

    @property
    def is_closed(self):
        """Check object is closed"""
        return self.status == self.CLOSED

    def close(self, request=None):
        return self._close(request)

    @transaction.atomic
    def _close(self, request=None):
        """Close the order"""
        signals.pre_close.send(
            sender=self.__class__,
            instance=self,
            actor=request.user,
            request=request,
        )
        self.status = self.CLOSED
        self.date_closed = timezone.now()
        self.save()
        signals.post_close.send(
            sender=self.__class__,
            instance=self,
            actor=request.user,
            request=request,
        )


class ArchiveAction(ActionMixin, models.Model):

    date_archived = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
        verbose_name=_("date archived"),
    )

    class Meta:
        abstract = True

    @property
    def is_archived(self):
        """Check order status is archived"""
        return self.status == self.ARCHIVED

    def archive(self, request=None):
        return self._archive(request)

    @transaction.atomic
    def _archive(self, request=None):
        """Archive the object"""
        signals.pre_archive.send(
            sender=self.__class__,
            instance=self,
            actor=request.user,
            request=request,
        )
        self.status = self.ARCHIVED
        self.date_archived = timezone.now()
        self.save()
        signals.post_archive.send(
            sender=self.__class__,
            instance=self,
            actor=request.user,
            request=request,
        )
