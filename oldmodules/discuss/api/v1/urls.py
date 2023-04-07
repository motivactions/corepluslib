from rest_framework.routers import DefaultRouter

from . import viewsets

router = DefaultRouter()
router.register("discuss", viewsets.DiscussViewSet, "discuss")

urlpatterns = [] + router.urls
