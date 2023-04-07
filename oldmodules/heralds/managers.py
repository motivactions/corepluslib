from django.db import models


class DirectMessageManager(models.Manager):
    def get_message_to(self, sender, recipient):
        qs = self.get_queryset()
        filters = models.Q(sender=sender, recipient=recipient) | models.Q(
            sender=recipient, recipient=sender
        )
        return qs.filter(filters)
