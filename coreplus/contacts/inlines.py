import nested_admin
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline

from .models import (
    BillingAddress,
    DeliverableAddress,
    LinkedAddress,
    LinkedContact,
    ShippingAddress,
)


class PublicPermission:
    def has_add_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True

    def has_view_permission(self, request, obj=None):
        return True


class BaseAddressInline(admin.StackedInline):
    pass


class LinkedAddressInline(PublicPermission, GenericStackedInline):
    model = LinkedAddress
    ct_field = "linked_object_type"
    ct_fk_field = "linked_object_id"
    extra = 0
    autocomplete_fields = ["country"]


class NestedLinkedAddressInline(
    PublicPermission,
    nested_admin.NestedGenericStackedInline,
):
    model = LinkedAddress
    ct_field = "linked_object_type"
    ct_fk_field = "linked_object_id"
    extra = 0
    autocomplete_fields = ["country"]


class LinkedContactInline(PublicPermission, GenericStackedInline):
    model = LinkedContact
    ct_field = "linked_object_type"
    ct_fk_field = "linked_object_id"
    extra = 0


class NestedLinkedContactInline(
    PublicPermission,
    nested_admin.NestedGenericStackedInline,
):
    model = LinkedContact
    ct_field = "linked_object_type"
    ct_fk_field = "linked_object_id"
    extra = 0


class SingleLinkedAddressInline(LinkedAddressInline):
    extra = 0
    max_num = 1
    autocomplete_fields = ["country"]


class BillingAddressInline(GenericStackedInline):
    model = BillingAddress
    ct_field = "content_type"
    ct_fk_field = "content_id"
    extra = 0
    max_num = 1
    autocomplete_fields = ["country"]


class NestedBillingAddressInline(NestedLinkedAddressInline):
    model = BillingAddress
    ct_field = "content_type"
    ct_fk_field = "content_id"
    extra = 0
    max_num = 1
    autocomplete_fields = ["country"]


class ShippingAddressInline(GenericStackedInline):
    model = ShippingAddress
    ct_field = "content_type"
    ct_fk_field = "content_id"
    extra = 0
    max_num = 1
    autocomplete_fields = ["country"]


class NestedShippingAddressInline(NestedLinkedAddressInline):
    model = ShippingAddress
    ct_field = "content_type"
    ct_fk_field = "content_id"
    extra = 0
    max_num = 1
    autocomplete_fields = ["country"]


class DeliverableAddressInline(GenericStackedInline):
    model = DeliverableAddress
    ct_field = "content_type"
    ct_fk_field = "content_id"
    extra = 0
    max_num = 1
    autocomplete_fields = ["country"]


class NestedDeliverableAddressInline(NestedLinkedAddressInline):
    model = DeliverableAddress
    ct_field = "content_type"
    ct_fk_field = "content_id"
    extra = 0
    max_num = 1
    autocomplete_fields = ["country"]
