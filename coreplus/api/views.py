from drf_spectacular.views import SpectacularAPIView as BaseSpectacularAPIView
from drf_spectacular.views import SpectacularRedocView as BaseSpectacularRedocView
from rest_framework.permissions import IsAdminUser

from .schemas import CustomSchemaGenerator


class SpectacularAPIView(BaseSpectacularAPIView):
    generator_class = CustomSchemaGenerator


class SpectacularRedocView(BaseSpectacularRedocView):
    pass
