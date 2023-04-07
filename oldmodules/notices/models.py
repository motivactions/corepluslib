from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mass_mail
from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _  # NOQA
from django.template.loader import render_to_string
from push_notifications.gcm import GCMDevice
from swapper import load_model

from .signals import bulk_notify, firebase_push_notify

User = get_user_model()


class NotificationPreference(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notice_preferences",
        verbose_name=_("User"),
    )

    email = models.BooleanField(
        default=True,
        help_text=_("Receive notification by email"),
    )
    push_notification = models.BooleanField(
        default=True,
        help_text=_("Receive notification by app"),
    )

    # Notification settings
    article_notification = models.BooleanField(
        default=True,
        verbose_name=_("Article Notice"),
        help_text=_("Receive article notification"),
    )

    class Meta:
        verbose_name = _("Notification Preference")
        verbose_name_plural = _("Notification Preferences")

    def __str__(self):
        return f"{self.user}"


class Broadcast(models.Model):
    EMAIL = "email"
    NOTIFICATION = "notification"
    ANDROID_NOTIFICATION = "android_notification"
    APPLE_NOTIFICATION = "apple_notification"
    ALL_MEDIA = "all"

    MEDIA_CHOICES = (
        (NOTIFICATION, _("Notification")),
        (EMAIL, _("Email")),
        (ANDROID_NOTIFICATION, _("Android Notification")),
        (ALL_MEDIA, _("All")),
    )

    title = models.CharField(
        max_length=255,
        verbose_name=_("title"),
        null=True,
        blank=True,
    )
    image = models.ImageField(
        null=True,
        blank=True,
        verbose_name=_("image"),
        help_text=_(
            "Make sure your image size atleast 1366x768px and 72 DPI resolution."
        ),
    )
    message = models.TextField(
        verbose_name=_("Message"),
        null=True,
        blank=True,
    )
    action_url = models.URLField(
        verbose_name=_("Action URL"),
    )
    action_title = models.CharField(
        max_length=255,
        verbose_name=_("Action Title"),
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
        verbose_name=_("created at"),
    )
    last_sent_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
        verbose_name=_("last sent"),
    )
    sent_counter = models.IntegerField(
        default=0,
        editable=False,
        verbose_name=_("Counter"),
    )
    media = models.CharField(
        max_length=255,
        default=NOTIFICATION,
        choices=MEDIA_CHOICES,
        verbose_name=_("media"),
    )
    users = models.ManyToManyField(
        User,
        blank=True,
        related_name="broadcasts",
        verbose_name=_("user"),
        help_text=_("Recipients"),
    )
    groups = models.ManyToManyField(
        Group,
        blank=True,
        related_name="broadcasts",
        verbose_name=_("group"),
        help_text=_("Group of recipients"),
    )

    class Meta:
        verbose_name = _("Broadcast")
        verbose_name_plural = _("Broadcasts")

    def __str__(self):
        return f"{self.title}"

    def _send_notification(self, actor, recipients, data):
        bulk_notify.send(
            self,
            actor=actor,
            verb="broadcast",
            recipients=recipients,
            **data,
        )

    def _send_firebase(self, recipients, data):
        firebase_push_notify.send(
            self,
            recipients=recipients,
            title=self.title,
            message=self.message,
            data=data,
        )

    def _send_email(self, recipients, data):
        # TODO find more eficient way to send mas email
        from django.conf import settings

        sender_email = getattr(
            settings,
            "DEFAULT_FROM_EMAIL",
            "My Domain <noreply@mydomain.com>",
        )

        recipient_emails = [
            user.email for user in recipients if user.email not in ["", None]
        ]
        email_content = render_to_string(
            template_name="notices/email_broadcast.txt",
            context={
                "title": self.title,
                "message": self.message,
                "data": data,
            },
        )
        messages = [(self.title, email_content, sender_email, recipient_emails)]
        send_mass_mail(messages)

    def get_title(self):
        return self.title

    def get_message(self):
        return self.message

    def get_data(self):
        data = {
            "type": "broadcast",
            "title": self.title,
            "message": self.message,
            "actions": {
                "url": self.action_url,
                "title": self.action_title,
            },
        }
        if bool(self.image):
            data["image"] = {
                "url": self.image.url,
                "width": self.image.width,
                "height": self.image.height,
            }
        return data

    def get_recipients(self):
        queryset = User.objects.filter(is_active=True)
        user_ids = [user.id for user in self.users.all()]
        group_query = models.Q(groups__in=self.groups.all())
        user_query = models.Q(id__in=user_ids)
        queryset = queryset.filter(group_query | user_query)
        return queryset

    def send(self, actor=None, **kwargs):
        recipients = self.get_recipients()

        # Get dictionary extra data
        data = self.get_data()
        data.update(kwargs)

        # Send web notification
        if self.media == self.EMAIL:
            self._send_email(recipients, data)
        elif self.media == self.ANDROID_NOTIFICATION:
            self._send_firebase(recipients, data)
        elif self.media == self.NOTIFICATION:
            self._send_notification(actor, recipients, data)
        elif self.media == self.ALL_MEDIA:
            self._send_email(recipients, data)
            self._send_firebase(recipients, data)
            self._send_notification(actor, recipients, data)
        else:
            return
        self.sent_counter += 1
        self.last_sent_at = timezone.now()
        self.save()


def bulk_notification_handler(verb, **kwargs):
    """
    Handler function to bulk create Notification instance upon action signal call.
    """

    EXTRA_DATA = True

    # Pull the options out of kwargs
    kwargs.pop("signal", None)
    kwargs.pop("sender")
    recipient = kwargs.pop("recipients")
    actor = kwargs.pop("actor")

    if actor is None:
        actor = User.objects.filter(is_superuser=True).first()

    optional_objs = [
        (kwargs.pop(opt, None), opt) for opt in ("target", "action_object")
    ]
    public = bool(kwargs.pop("public", True))
    description = kwargs.pop("description", None)
    timestamp = kwargs.pop("timestamp", timezone.now())
    Notification = load_model("notifications", "Notification")
    level = kwargs.pop("level", Notification.LEVELS.info)

    # Check if User or Group
    if isinstance(recipient, Group):
        recipients = recipient.user_set.all()
    elif isinstance(recipient, (QuerySet, list)):
        recipients = recipient
    else:
        recipients = [recipient]

    new_notifications = []

    for recipient in recipients:
        newnotify = Notification(
            recipient=recipient,
            actor_content_type=ContentType.objects.get_for_model(actor),
            actor_object_id=actor.pk,
            verb=str(verb),
            public=public,
            description=description,
            timestamp=timestamp,
            level=level,
        )

        # Set optional objects
        for obj, opt in optional_objs:
            if obj is not None:
                setattr(newnotify, "%s_object_id" % opt, obj.pk)
                setattr(
                    newnotify,
                    "%s_content_type" % opt,
                    ContentType.objects.get_for_model(obj),
                )

        # extra data as json data
        if kwargs and EXTRA_DATA:
            newnotify.data = kwargs

        new_notifications.append(newnotify)

    results = Notification.objects.bulk_create(new_notifications)
    return results


def firebase_notification_handler(recipients, title, message, **kwargs):
    kwargs.pop("signal", None)
    kwargs.pop("sender", None)
    recipient_ids = [user.id for user in recipients]
    gcm_devices = GCMDevice.objects.filter(user_id__in=recipient_ids, active=True)
    print(gcm_devices)
    try:
        gcm_devices.send_message(message, title=title, payload=kwargs)
    except Exception as err:
        print(err)


# Connect the signal
bulk_notify.connect(
    bulk_notification_handler, dispatch_uid="notifications.models.notification"
)


firebase_push_notify.connect(
    firebase_notification_handler, dispatch_uid="push_notification.gcm.firebase"
)
