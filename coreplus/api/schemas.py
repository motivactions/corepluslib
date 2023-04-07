from drf_spectacular.generators import SchemaGenerator
from drf_spectacular.openapi import AutoSchema


class CustomAutoSchema(AutoSchema):
    def get_tags(self):
        tags = super().get_tags()
        return tags


class CustomSchemaGenerator(SchemaGenerator):
    pass
