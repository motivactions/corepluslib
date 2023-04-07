from django.urls import path
from rest_framework.routers import DefaultRouter

from .viewsets import CategoryViewSet, TagViewSet

router = DefaultRouter()
router.register("tag", TagViewSet, "tag")
router.register("category", CategoryViewSet, "category")

urlpatterns = []

urlpatterns += router.urls
