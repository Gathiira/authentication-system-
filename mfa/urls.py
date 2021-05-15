from rest_framework.routers import DefaultRouter

from mfa.views import OtpView

router = DefaultRouter(trailing_slash=False)

router.register("otp", OtpView, basename='otp')

urlpatterns = router.urls
