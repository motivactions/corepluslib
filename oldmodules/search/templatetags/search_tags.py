from django.template import Library
from haystack.forms import FacetedSearchForm

register = Library()


@register.inclusion_tag("search/search_form.html", takes_context=True)
def search_form(context, form_kwargs=None, searchqueryset=None, placeholder="Search"):
    request = context.get("request")
    data = None
    kwargs = {"load_all": True}
    if form_kwargs:
        kwargs.update(form_kwargs)
    if len(request.GET):
        data = request.GET
    if searchqueryset is not None:
        kwargs["searchqueryset"] = searchqueryset
    return {
        "form": FacetedSearchForm(data, **kwargs),
        "placeholder": placeholder,
        "request": request,
    }
