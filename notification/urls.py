from rest_framework.routers import DefaultRouter

from notification.views import EmailViewSet

router = DefaultRouter(trailing_slash=False)

router.register("email", EmailViewSet, basename='email')

urlpatterns = router.urls
