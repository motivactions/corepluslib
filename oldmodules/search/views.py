from pprint import pprint  # NOQA

from django.apps import apps
from django.conf import settings
from django.views.generic import TemplateView
from haystack.forms import SearchForm
from haystack.views import FacetedSearchView as BaseSearchView


class SearchView(BaseSearchView):
    """Haystack Search View"""

    pass


class AlgoliaSearchView(TemplateView):
    """Algolia Search View"""

    form_class = SearchForm
    template_name = "search/algolia_search.html"
    params = {"hitsPerPage": 5}

    def dispatch(self, request, *args, **kwargs):
        form = self.get_form()
        form.is_valid()
        self.query = form.cleaned_data.get("q", None)
        self.models = form.cleaned_data.get("models", None)
        return super().dispatch(request, *args, **kwargs)

    def get_registered_models(self):
        from algoliasearch_django import algolia_engine

        registered_models = algolia_engine.get_registered_models()
        return registered_models

    def get_form(self):
        form = self.form_class(self.get_form_kwargs())
        return form

    def get_form_kwargs(self, **kwargs):
        return self.request.GET

    def get_search_results(self):
        from algoliasearch_django import algolia_engine

        search_results = {}
        if self.query in ["", None]:
            return search_results
        if not self.models:
            models = self.get_registered_models()
        else:
            models = [apps.get_model(model) for model in self.models]
        for model in models:
            search_results[model._meta.model_name] = algolia_engine.raw_search(
                model, self.query, self.params
            )
        return search_results

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        search_results = self.get_search_results()
        search_form = self.get_form()
        kwargs.update(
            {
                "q": self.query,
                "models": self.models,
                "form": search_form,
                "search_results": search_results,
            }
        )
        return kwargs


def search_view(request, *args, **kwargs):
    if settings.SEARCH_ENGINE == "algolia":
        return AlgoliaSearchView.as_view()(request, *args, **kwargs)
    else:
        return SearchView()(request, *args, **kwargs)
