from django.db import models


class TagManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()
