from django.contrib.auth import get_user_model

from rest_framework import serializers

User = get_user_model()


class CorePlusUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
