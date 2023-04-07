from rest_framework.routers import DefaultRouter

from . import viewsets

router = DefaultRouter()
router.register("image", viewsets.FilerImageViewSet, "image")
router.register("audio-visual", viewsets.FilerAudioVisualViewSet, "audio_visual")
router.register("file", viewsets.FilerFileViewSet, "file")
urlpatterns = [] + router.urls
