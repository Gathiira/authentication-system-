from rest_framework.routers import DefaultRouter

from authentication.views import authentication_views, citizen_account_views


router = DefaultRouter(trailing_slash=False)


auth_url = 'auth'
router.register(
    auth_url, authentication_views.AuthenticationViewSet, basename='auth')
router.register(
    auth_url, citizen_account_views.CitizenAccountViewSet, basename='auth')

urlpatterns = router.urls
