from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView

from ..helpers import get_apiview, get_router, get_urls

app_name = "v2"


paths = get_urls("API_V2_URL_PATTERNS")
viewset = get_router("API_V2_VIEWSET_HOOK")
apiviews = get_apiview("API_V2_VIEW_HOOK")

urlpatterns = (
    [
        path("schema/", SpectacularAPIView.as_view(), name="schema"),
        path(
            "documentation/",
            SpectacularRedocView.as_view(url_name="v2:schema"),
            name="redoc",
        ),
    ]
    + paths
    + viewset.urls
    + apiviews
)
