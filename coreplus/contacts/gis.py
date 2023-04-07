from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _


class GeoLocationModel(models.Model):
    point = models.PointField(
        null=True,
        blank=True,
        help_text=_("Geolocation Point"),
    )

    class Meta:
        abstract = True

    @property
    def longitude(self):
        return None if self.point is None else self.point[0]

    @property
    def latitude(self):
        return None if self.point is None else self.point[1]
