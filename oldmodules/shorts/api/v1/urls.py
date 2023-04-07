from rest_framework.routers import DefaultRouter

from . import viewsets

router = DefaultRouter()
router.register("shorturl", viewsets.ShortUrlViewSet, "shorturl")

urlpatterns = [] + router.urls
