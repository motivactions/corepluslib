from rest_framework.routers import DefaultRouter

from . import viewsets

router = DefaultRouter()
router.register("direct-message", viewsets.DirectMessageViewSet, "direct_message")

urlpatterns = [] + router.urls
