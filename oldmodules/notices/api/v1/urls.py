from push_notifications.api.rest_framework import (
    APNSDeviceAuthorizedViewSet,
    GCMDeviceAuthorizedViewSet,
    WebPushDeviceAuthorizedViewSet,
)
from rest_framework.routers import DefaultRouter

from coreplus.notices.api.v1.viewsets import NotificationViewSet

router = DefaultRouter()
router.register("apnsdevice", APNSDeviceAuthorizedViewSet, "apnsdevice")
router.register("gcmdevice", GCMDeviceAuthorizedViewSet, "gcmdevice")
router.register("webpushdevice", WebPushDeviceAuthorizedViewSet, "webpushdevice")
router.register("notification", NotificationViewSet, "notification")

urlpatterns = [] + router.urls
