from django.conf import settings
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from notifications.models import Notification
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, mixins

from .serializers import NotificationSerializer


class NotificationViewSet(mixins.DestroyModelMixin, ReadOnlyModelViewSet):
    queryset = Notification.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(recipient=self.request.user)

    @extend_schema(operation_id="notices_mark_as_read_all")
    @action(methods=["GET"], url_path="mark-all-as-read", detail=False)
    def mark_as_read_all(self, request, *args, **kwargs):
        self.request.user.notifications.mark_all_as_read()
        return Response(data={"message": "success"})

    @extend_schema(operation_id="notices_mark_as_read")
    @action(methods=["GET"], url_path="mark-as-read", detail=True)
    def mark_as_read(self, request, id, *args, **kwargs):
        notification = get_object_or_404(Notification, recipient=request.user, id=id)
        notification.mark_as_read()
        return Response(data={"message": "success"})

    @extend_schema(operation_id="notices_mark_as_unread")
    @action(methods=["GET"], url_path="mark-as-unread", detail=True)
    def mark_as_unread(self, request, id, *args, **kwargs):
        notification = get_object_or_404(Notification, recipient=request.user, id=id)
        notification.mark_as_unread()
        return Response(data={"message": "success"})

    def perform_destroy(self, instance):
        if settings.get_config()["SOFT_DELETE"]:
            instance.deleted = True
            instance.save()
        else:
            instance.delete()
        return Response(data={"message": "success"})
