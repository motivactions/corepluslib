from django.db import models


class ShortUrlManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()
