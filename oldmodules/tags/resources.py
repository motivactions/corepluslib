from import_export.fields import Field
from import_export.resources import ModelResource
from import_export.widgets import CharWidget, ForeignKeyWidget

from .models import Category


class CategoryResource(ModelResource):
    slug = Field(
        attribute="slug",
        readonly=True,
        column_name="slug",
        widget=CharWidget(),
    )
    parent = Field(
        attribute="parent",
        column_name="parent",
        widget=ForeignKeyWidget(Category, field="slug"),
    )

    class Meta:
        model = Category
        exclude = ("lft", "rght", "tree_id", "level")
        export_order = ("id", "name", "slug", "parent")
        import_id_fields = ("slug",)
