from rest_framework.routers import DefaultRouter
from .views import KeywordViewset, ContentItemViewSet, import_content_view, FlagViewSet, scan_view
from django.urls import path


router = DefaultRouter()
router.register(r'keywords', KeywordViewset)
router.register(r'content-items', ContentItemViewSet)
router.register(r'flags', FlagViewSet)

urlpatterns = router.urls

urlpatterns += [
    path('import-content/', import_content_view),
    path('scan/', scan_view)
]
