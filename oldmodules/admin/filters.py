from django.contrib.admin.filters import SimpleListFilter
from django.utils.translation import gettext_lazy as _


class PreFilteredListFilter(SimpleListFilter):

    # Either set this or override .get_default_value()
    default_value = None

    no_filter_value = "all"
    no_filter_name = _("All")

    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = None

    # Parameter for the filter that will be used in the URL query.
    parameter_name = None

    def get_default_value(self):
        if self.default_value is not None:
            return self.default_value
        raise NotImplementedError(
            "Either the .default_value attribute needs to be set or "
            "the .get_default_value() method must be overridden to "
            "return a URL query argument for parameter_name."
        )
