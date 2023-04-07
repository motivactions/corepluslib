from drf_spectacular.extensions import OpenApiSerializerFieldExtension
from drf_spectacular.plumbing import build_basic_type
from drf_spectacular.types import OpenApiTypes


class TagListSerializerFieldExtension(OpenApiSerializerFieldExtension):
    target_class = "taggit.serializers.TagListSerializerField"

    def map_serializer_field(self, auto_schema, direction):
        return build_basic_type(OpenApiTypes.STR)
