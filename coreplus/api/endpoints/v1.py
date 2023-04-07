from django.urls import path

from ..helpers import get_apiview, get_router, get_urls
from ..views import SpectacularAPIView, SpectacularRedocView

app_name = "v1"


paths = get_urls("API_V1_URL_PATTERNS")
viewset = get_router("API_V1_VIEWSET_HOOK")
apiviews = get_apiview("API_V1_VIEW_HOOK")

urlpatterns = (
    [
        path("schema/", SpectacularAPIView.as_view(), name="schema"),
        path(
            "documentation/",
            SpectacularRedocView.as_view(url_name="v1:schema"),
            name="redoc",
        ),
    ]
    + paths
    + viewset.urls
    + apiviews
)
