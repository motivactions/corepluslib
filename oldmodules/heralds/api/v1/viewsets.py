import logging

from django.apps import apps as django_apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from filer.models import File
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from coreplus.reactions.api.v1.serializers import (
    ReactionableModelAddSerializer,
    ReactionSerializer,
)
from coreplus.reactions.models import Reaction

from ...models import DirectMessage, DirectMessageAttachment
from .serializers import (
    AttachmentSerializer,
    DirectMessageCreateSerializer,
    DirectMessageSerializer,
)

logger = logging.getLogger(__name__)
User = get_user_model()


class DirectMessageViewSet(ModelViewSet):
    queryset = DirectMessage.objects.all()
    serializer_class = DirectMessageSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ["@content"]
    filterset_fields = ["sender", "recipient"]

    def get_serializer_class(self):
        if self.action == "create":
            return DirectMessageCreateSerializer
        elif self.action == "add_attachment":
            return AttachmentSerializer
        elif self.action == "get_user_reaction":
            return ReactionSerializer
        elif self.action == "add_direct_message_reaction":
            return ReactionableModelAddSerializer
        return super().get_serializer_class()

    @extend_schema(operation_id="direct_message_list")
    def list(self, request, *args, **kwargs):
        """
        - Search parameter will do a full text search based on **content**
        - Can filter posts based on the **sender** or **recipient**
        """
        return super().list(request, *args, **kwargs)

    @extend_schema(operation_id="direct_message_retrieve")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        operation_id="direct_message_create",
        request=DirectMessageCreateSerializer,
        responses=DirectMessageSerializer,
    )
    def create(self, request, *args, **kwargs):
        """
        Create new direct message
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        attachment_ids = serializer.validated_data.pop("attachment_ids", None)
        if attachment_ids:
            obj = self.perform_create_with_attachment(serializer, attachment_ids)
        else:
            obj = self.perform_create(serializer)

        resp_serializers = DirectMessageSerializer(
            instance=obj, context=self.get_serializer_context()
        )
        headers = self.get_success_headers(serializer.data)
        return Response(
            resp_serializers.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        obj = serializer.save(sender=self.request.user)
        logger.info(_("Created a new direct message"))
        return obj

    def perform_create_with_attachment(self, serializer, attachment_ids):
        """
        Function to create direct message with attachment
        """
        try:
            with transaction.atomic():
                obj = serializer.save(sender=self.request.user)
                attachments = []
                for attachment_id in attachment_ids:
                    attachments.append(
                        DirectMessageAttachment(
                            direct_message=obj,
                            attachment=File.objects.get(id=attachment_id),
                        )
                    )
                DirectMessageAttachment.objects.bulk_create(attachments)
            return obj

        except Exception:
            logger.error(_("Failed to create direct message"))
            raise ValidationError(_("Failed to create direct message"))

    @extend_schema(operation_id="direct_message_update")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(operation_id="direct_message_update_partial")
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(operation_id="direct_message_destroy")
    def destroy(self, request, *args, **kwargs):
        """
        > **NOTES:** also delete the file and attachments related to the direct message
        """
        obj = self.get_object()
        for attachment in obj.attachments.all():
            django_apps.get_model(
                settings.FILER_IMAGE_MODEL, require_ready=False
            ).objects.get(id=attachment.attachment.id).delete()
        logger.info(_("Direct message deleted"))
        return super().destroy(request, *args, **kwargs)

    @extend_schema(operation_id="direct_message_recipients")
    @action(
        methods=["GET"], url_path="get-recipient/(?P<recipient_id>[^/.]+)", detail=False
    )
    def get_recipient(self, request, *args, **kwargs):
        """
        Get list of direct messages related to the sender and recipient
        """
        recipient_id = int(kwargs.get("recipient_id", None))
        if request.user.id == recipient_id:
            raise ValidationError(_("current user could not be the recipient"))
        recipient = get_object_or_404(User, id=recipient_id)
        messages = DirectMessage.objects.get_message_to(self.request.user, recipient)
        unread_messages = messages.filter(
            recipient=self.request.user, status=DirectMessage.UNREAD
        )
        for obj in unread_messages:
            obj.status = DirectMessage.READ
            obj.save()

        self.filter_backends = [OrderingFilter]
        self.ordering_fields = ["pk", "created"]
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, messages, self)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(data=serializer.data)

    @extend_schema(operation_id="direct_message_reactions")
    @action(methods=["GET"], url_path="reaction", detail=True)
    def get_user_reaction(self, request, pk=None, *args, **kwargs):
        """
        Get current user reaction related to the direct message
        """
        message = self.get_object()
        user_reaction = message.get_user_reaction(request.user)
        serializer = self.get_serializer(user_reaction, many=False)
        return Response(data=serializer.data)

    @extend_schema(
        operation_id="direct_message_reaction_add",
        request=ReactionableModelAddSerializer,
        responses=ReactionSerializer,
    )
    @action(methods=["POST"], url_path="add-reaction", detail=True)
    def add_direct_message_reaction(self, request, pk=None, *args, **kwargs):
        """
        Add a reaction to a direct message.
        Required data = {"value":"(reaction_type)"}
        """
        obj = self.get_object()
        value = request.data.get("value")

        if (value, value) in Reaction.REACTION_TYPES:
            reaction = obj.add_reaction(request.user, value)
            reaction_serializer = ReactionSerializer(reaction, many=False)
            logger.info(_("Added reaction to a direct message"))
            return Response(data=reaction_serializer.data)
        else:
            return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    @extend_schema(operation_id="direct_message_reaction_delete")
    @action(methods=["DELETE"], url_path="delete-reaction", detail=True)
    def delete_direct_message_reaction(self, request, pk=None, *args, **kwargs):
        """
        Delete a reaction from a direct message
        """
        obj = self.get_object()
        user_reaction = obj.get_user_reaction(request.user)
        if user_reaction:
            user_reaction.delete()
            logger.info(_("Deleted reaction from a direct message"))
        return Response(status=status.HTTP_204_NO_CONTENT)
