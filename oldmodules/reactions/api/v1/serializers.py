from rest_framework import serializers

from coreplus.configs import coreplus_configs

from ...models import Flag, Reaction, Review

UserSerializer = coreplus_configs.DEFAULT_USER_SERIALIZER


class ReactionSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)

    class Meta:
        model = Reaction
        fields = "__all__"


class ReactionableModelSerializer(serializers.ModelSerializer):
    user_reaction = serializers.SerializerMethodField(required=False)

    def get_user_reaction(self, obj) -> ReactionSerializer:
        user = self.context.get("request").user
        return ReactionSerializer(instance=obj.user_reaction(user)).data


class ReactionableModelAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reaction
        fields = ["value"]


class FlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flag
        fields = "__all__"


class FlaggableModelAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flag
        fields = ["value", "message"]


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["rating", "message"]
