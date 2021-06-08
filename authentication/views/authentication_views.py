import logging
import requests
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action

from django.contrib.auth import authenticate, get_user_model
from django.apps import apps as system_apps
from django.conf import settings

from oauth2_provider.models import get_application_model, get_refresh_token_model
from oauth2_provider.views.generic import ProtectedResourceView


from authentication import serializers as auth_serializers
from shared_functions import (
    service_responses, time_functions, authsystemuser, system_utils)

service_response = service_responses.ServiceResponseManager()
time_function = time_functions
system_util = system_utils.SystemServiceManager()
oauth2user = authsystemuser.ApplicationUser()

application_label = 'authentication'
log = logging.getLogger(__name__)


class AuthenticationViewSet(viewsets.ViewSet):
    permission_classes = (permissions.AllowAny, )

    @action(
        methods=['POST'],
        detail=False,
        url_path='login',
        url_name='login'
    )
    def login(self, request):
        payload = request.data
        serializer = auth_serializers.LoginSerializer(data=payload)
        if serializer.is_valid(raise_exception=True):
            phone_number = serializer.data.get("phone_number")
            password = serializer.data.get("password")
            account_usertype = serializer.data.get("usertype")

            user = authenticate(phone_number=phone_number, password=password)
            if not bool(user):
                return Response(
                    {"details": "invalid phone number or password. If registered, Kinldy consider validating your phone number."},
                    status=status.HTTP_401_UNAUTHORIZED)

            user_instance = get_user_model().objects.get(phone_number=phone_number)
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
                log.info(e)
                return Response(
                    {"details": "Invalid app mapper"},
                    status=status.HTTP_401_UNAUTHORIZED)

            try:
                reference_model.objects.get(
                    userid_id=user_instance)
            except Exception as e:
                log.info(e)
                return Response(
                    {"details": "Invalid user profile"},
                    status=status.HTTP_401_UNAUTHORIZED)

            # send_otp_to_email]
            otp_payload = {
                "user": str(user_instance.id),
                "send_to": phone_number,
                "mode": "sms",
                "module": "VERIFICATION_CODE",
                "expiry_time": settings.OTP_EXPIRY_TIME
            }
            otp_generated, otp_response = service_response.generate_otp_code(
                otp_payload)

            if not otp_generated:
                return Response(
                    {"details": "Otp generation failed"},
                    status=status.HTTP_400_BAD_REQUEST)
            app_otp_code = otp_response['code']

            # send sms
            sms_payload = {
                "phone": phone_number,
                "message": f"Your login verification code is: {app_otp_code}"
            }

            # sending_sms = service_response.send_bulk_sms(sms_payload)
            # if not sending_sms:
            #     return Response(
            #         {"details": "Failed to send sms. Check your phone number."},
            #         status=status.HTTP_401_UNAUTHORIZED)

            if not settings.DEBUG:
                app_otp_code = None
            return Response(
                {
                    "details": "Otp generated successfully",
                    "otp_code": app_otp_code
                })
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


class AuthorizationViewSet(ProtectedResourceView, viewsets.ViewSet):
    permission_classes = (permissions.IsAuthenticated, )

    @action(
        methods=['GET'],
        detail=False,
        url_path='auth-status',
        url_name='auth-status'
    )
    def authentication_status(self, request):
        return Response({"details": "success"})

    @action(methods=["POST"],
            detail=False,
            url_path="logout",
            url_name="logout")
    def logout(self, request):
        authorization_token = request.headers.get('Authorization', b'')
        auth_token = authorization_token.split()
        logged_in_user = request.user
        logout_status, message = system_util.logout_user(
            request, auth_token[1], logged_in_user)
        if logout_status:
            return Response({"details": message}, status=status.HTTP_200_OK)
        return Response({"details": message}, status=status.HTTP_200_OK)

    @action(methods=["POST"],
            detail=False,
            url_path="refresh-token",
            url_name="refresh-token")
    def refresh_token(self, request):
        payload = request.data
        serializer = auth_serializers.RefreshTokenSerializer(
            data=payload, many=False)
        if serializer.is_valid():
            refresh_token = payload['refresh_token']
            refresh_token_details = get_refresh_token_model(). \
                objects.filter(token=refresh_token)
            refresh_token_exists = refresh_token_details.exists()
            if refresh_token_exists:
                refresh_token_user = refresh_token_details.first()
                token_user = refresh_token_user.user_id
                selected_user = get_application_model().objects.get(user_id=token_user)
                server_address = service_response.get_current_server_url(
                    request)
                oauth2_url = server_address + '/o/token/'
                r = requests.post(
                    oauth2_url,
                    data={
                        'grant_type': 'refresh_token',
                        'client_id': selected_user.client_id,
                        'client_secret': selected_user.client_secret,
                        'refresh_token': refresh_token
                    },
                )
                responsedata = r.json()
                if r.status_code == 200:
                    userinfo = {
                        "access_token": responsedata['access_token'],
                        "expires_in": responsedata['expires_in'],
                        "token_type": responsedata['token_type'],
                        "refresh_token": responsedata['refresh_token'],
                        "jwt": oauth2user.generate_jwt_token(token_user)
                    }
                    return Response(
                        {'details': userinfo},
                        status=status.HTTP_200_OK)
                else:
                    return Response(
                        {'details': responsedata['error']},
                        status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response(
                    {'details': 'Invalid Refresh Token Passed'},
                    status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({'details': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)
