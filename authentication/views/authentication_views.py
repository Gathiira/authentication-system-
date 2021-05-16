import logging
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action

from django.contrib.auth import authenticate, get_user_model
from django.apps import apps as system_apps
from django.conf import settings


from authentication import serializers as auth_serializers
from shared_functions import service_responses, time_functions

service_response = service_responses.ServiceResponseManager()
time_function = time_functions

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
