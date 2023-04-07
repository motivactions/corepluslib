from django.urls import path

from .views import redirect_view

urlpatterns = [path("<str:shortened_part>/", redirect_view)]
