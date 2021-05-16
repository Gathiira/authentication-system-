import logging
import requests
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action

from django.contrib.auth import authenticate, get_user_model
from django.apps import apps as system_apps
from django.conf import settings

from oauth2_provider.models import get_application_model, get_refresh_token_model


from authentication import serializers as auth_serializers
from shared_functions import service_responses, time_functions, authsystemuser

service_response = service_responses.ServiceResponseManager()
time_function = time_functions
oauth2user = authsystemuser.ApplicationUser()

application_label = 'authentication'
log = logging.getLogger(__name__)


class AuthenticationViewSet(viewsets.ModelViewSet):
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
            email = serializer.data.get("email")
            password = serializer.data.get("password")
            account_usertype = serializer.data.get("usertype")

            user = authenticate(email=email, password=password)
            if not bool(user):
                return Response(
                    {"details": "invalid email or password. If registered, Kinldy consider validating your email."},
                    status=status.HTTP_401_UNAUTHORIZED)

            user_instance = get_user_model().objects.get(email=email)
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
                user_details = reference_model.objects.get(
                    userid_id=user_instance)
            except Exception as e:
                log.info(e)
                return Response(
                    {"details": "Invalid user profile"},
                    status=status.HTTP_401_UNAUTHORIZED)

            # send_otp_to_email]
            otp_payload = {
                "user": str(user_instance.id),
                "send_to": email,
                "mode": "email",
                "module": "LOGIN",
                "expiry_time": settings.OTP_EXPIRY_TIME
            }
            otp_generated, otp_response = service_response.generate_otp_code(
                otp_payload)

            if not otp_generated:
                return Response(
                    {"details": "Otp generation failed"},
                    status=status.HTTP_400_BAD_REQUEST)
            app_otp_code = otp_response['code']

            notification_payload = {
                "subject": "LOGIN VERIFICATION CODE",
                "recipients": [email],
                "message": f"Your login verification code is {app_otp_code}",
            }
            #  send email

            sending_mail = service_response.send_email(notification_payload)
            if not sending_mail:
                return Response(
                    {"details": "Failed to send mail. Check your mail or internet connection"},
                    status=status.HTTP_401_UNAUTHORIZED)

            if not settings.DEBUG:
                app_otp_code = None
            return Response(
                {
                    "details": "Otp generated successfully",
                    "otp_code": app_otp_code
                })
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    @action(
        methods=['POST'],
        detail=False,
        url_path='verify-login-otp',
        url_name='verify-login-otp'
    )
    def verify_login_otp(self, request):
        payload = request.data
        serializer = auth_serializers.VerifyLoginOtpSerializer(data=payload)
        if serializer.is_valid(raise_exception=True):
            email = serializer.data.get("email")
            password = serializer.data.get("password")
            otp_code = serializer.data.get("otp_code")

            try:
                user_details = get_user_model().objects.get(email=email)
            except Exception as e:
                log.error(e)
                return Response(
                    {"details": "User not found"},
                    status=status.HTTP_404_NOT_FOUND)

            otp_params = {
                "user_id": str(user_details.id),
                "otp_code": otp_code,
                "module": "LOGIN"
            }

            validated_otp, response_inf = service_response.verify_otp_code(
                otp_params)
            print(response_inf)
            if not validated_otp:
                return Response(
                    {"details": response_inf['details']},
                    status=status.HTTP_400_BAD_REQUEST)

            user = authenticate(email=email, password=password)
            if not bool(user):
                return Response(
                    {"details": "Invalid email or password"},
                    status=status.HTTP_401_UNAUTHORIZED)
            try:
                selected_user = get_application_model().objects.get(user=user_details)
            except Exception as e:
                log.error(e)
                return Response(
                    {"details": "Invalid credentials"},
                    status=status.HTTP_401_UNAUTHORIZED)
            server_address = service_response.get_resource_server()

            r = requests.post(
                server_address,
                data={
                    "grant_type": 'password',
                    'username': email,
                    "password": password,
                    'client_id': selected_user.client_id,
                    'client_secret': selected_user.client_secret
                }
            )

            response_data = r.json()
            if r.status_code != 200:
                return Response(
                    {"details": response_data['error_description']},
                    status=status.HTTP_401_UNAUTHORIZED)
            user_info = {
                "access_token": response_data['access_token'],
                "expires_in": response_data['expires_in'],
                "token_type": response_data['token_type'],
                "refresh_token": response_data['refresh_token'],
                "jwt": oauth2user.generate_jwt_token(user_details.id)
            }
            return Response({"details": user_info}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
