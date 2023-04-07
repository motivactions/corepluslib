import logging

from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from coreplus.reactions.api.v1.serializers import (
    FlaggableModelAddSerializer,
    FlagSerializer,
    ReactionableModelAddSerializer,
    ReactionSerializer,
)
from coreplus.reactions.models import Flag, Reaction

from ...models import Discuss
from .serializers import DiscussSerializer

logger = logging.getLogger(__name__)


class DiscussViewSet(ModelViewSet):
    queryset = Discuss.objects.all()
    serializer_class = DiscussSerializer

    def get_serializer_class(self):
        if self.action == "add_discuss_reaction":
            return ReactionableModelAddSerializer
        elif self.action == "add_discuss_flag":
            return FlaggableModelAddSerializer
        return super().get_serializer_class()

    @extend_schema(operation_id="discuss_list")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(operation_id="discuss_retrieve")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(operation_id="discuss_create")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(operation_id="discuss_update")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(operation_id="discuss_update_partial")
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(operation_id="discuss_destroy")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        operation_id="discuss_reaction_add",
        request=ReactionableModelAddSerializer,
        responses=ReactionSerializer,
    )
    @action(methods=["POST"], url_path="add-reaction", detail=True)
    def add_discuss_reaction(self, request, pk=None, *args, **kwargs):
        """
        Add a reaction to a discuss.
        Required data = {"value":"(reaction_type)"}
        """
        obj = self.get_object()
        value = request.data.get("value")

        if (value, value) in Reaction.REACTION_TYPES:
            reaction = obj.add_reaction(request.user, value)
            reaction_serializer = ReactionSerializer(
                reaction,
                many=False,
                context=self.get_serializer_context(),
            )
            logger.info(_("Added reaction to a discuss"))
            return Response(data=reaction_serializer.data)
        else:
            return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    @extend_schema(
        operation_id="discuss_reaction_delete",
    )
    @action(methods=["DELETE"], url_path="delete-reaction", detail=True)
    def delete_club_post_discuss_reaction(self, request, pk=None, *args, **kwargs):
        """
        Delete a reaction from a discuss
        """
        obj = self.get_object()
        user_reaction = obj.get_user_reaction(request.user)
        if user_reaction:
            user_reaction.delete()
            logger.info(_("Deleted reaction from a discuss"))
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        operation_id="discuss_flag_add",
        request=FlaggableModelAddSerializer,
        responses=FlagSerializer,
    )
    @action(methods=["POST"], url_path="add-flag", detail=True)
    def add_discuss_flag(self, request, pk=None, *args, **kwargs):
        """
        Add a flag to a club.
        Required data = {"value":"(flag_type)"}
        """
        obj = self.get_object()
        value = request.data.get("value")

        if (value, value) in Flag.FLAG_TYPES:
            flag = obj.add_flag(request.user, value, request.data.get("message"))
            flag_serializer = FlagSerializer(flag, many=False)
            logger.info(_("Added flag to a club"))
            return Response(data=flag_serializer.data)
        else:
            return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)
