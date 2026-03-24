from rest_framework.routers import DefaultRouter
from .views import KeywordViewset

router = DefaultRouter()
router.register(r'keywords', KeywordViewset)

urlpatterns = [
     router.urls
]
