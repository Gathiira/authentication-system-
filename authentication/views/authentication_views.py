from rest_framework import serializers, viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from django.contrib.auth import authenticate, get_user_model
from django.apps import apps as system_apps
from django.conf import settings


from authentication import serializers as auth_serializers

application_label = 'authentication'

log = settings.application_logger


class AuthenticationViewSet(viewsets.ViewSet):

    @action(
        methods=['POST'],
        detail=False,
        url_path='login',
        url_name='login'
    )
    def login(self, request):
        payload = request.data
        payload_serializer = auth_serializers.LoginSerializer(data=payload)
        if payload_serializer.is_valid(raise_exception=True):
            username = serializers.data.get("username")
            password = serializers.data.get("password")
            account_usertype = serializers.data.get("usertype")

            user = authenticate(username=username, password=password)
            if not bool(user):
                return Response(
                    {"details": "invalid username or password"},
                    status=status.HTTP_401_UNAUTHORIZED)

            user_instance = get_user_model().objects.get(username=username)
            user_category_type = user_instance.usertype
            user_category = user_category_type.category
            user_category_mapping = user_category.user_mapping
            if account_usertype != user_category_mapping:
                return Response({"details": "Invalid user account"})

            app_model = user_category_type.model_name
            if not bool(app_model):
                return Response({"details": "Invalid user mapping"})

            try:
                reference_model = system_apps.get_model(
                    application_label, app_model, require_ready=True)
            except Exception as e:
                print(e)
                return Response(
                    {"details": "Invalid app mapper"},
                    status=status.HTTP_401_UNAUTHORIZED)

            try:
                user_details = reference_model.objects.get(
                    userid_id=user_instance)
            except Exception as e:
                print(e)
                return Response(
                    {"details": "Invalid user profile"},
                    status=status.HTTP_401_UNAUTHORIZED)
