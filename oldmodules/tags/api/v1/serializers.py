from typing import Optional

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from djoser.serializers import UserSerializer as BaseUserSerializer
from rest_framework import serializers

from ...models import Category, Tag


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class TagSerializer(serializers.Serializer):
    class Meta:
        model = Tag
        fields = "__all__"
