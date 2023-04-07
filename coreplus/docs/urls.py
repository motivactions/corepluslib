from django.urls import path, re_path

from .views import DOCS_DIRHTML, DocsRootView, HomepageView, serve_docs

urlpatterns = [
    path("", HomepageView.as_view(), name="docs_homepage"),
]


if not DOCS_DIRHTML:
    urlpatterns += [
        re_path(r"^content/$", DocsRootView.as_view(permanent=True), name="docs_root"),
    ]

urlpatterns += [
    re_path(r"^content/(?P<path>.*)$", serve_docs, name="docs_files"),
]
