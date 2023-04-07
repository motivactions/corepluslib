from django.shortcuts import render
from django.urls import path
from django.urls.conf import include

urlpatterns = [
    path("v1/", include("coreplus.api.endpoints.v1")),
    path("v2/", include("coreplus.api.endpoints.v2")),
]
