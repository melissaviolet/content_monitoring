from rest_framework.routers import DefaultRouter
from .views import KeywordViewset, import_content_view
from django.urls import path


router = DefaultRouter()
router.register(r'keywords', KeywordViewset)

urlpatterns = router.urls

urlpatterns += [
    path('import-content/', import_content_view)
]
