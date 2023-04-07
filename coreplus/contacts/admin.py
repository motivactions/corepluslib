from django.contrib import admin

from .models import Country


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ["__str__", "display_order"]
    list_filter = ["is_shipping_country"]
    search_fields = ["name", "printable_name", "iso_3166_1_a2", "iso_3166_1_a3"]
