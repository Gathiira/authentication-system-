import logging
import requests
from django.contrib.auth.models import Group
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action

from oauth2_provider.models import get_application_model
from django.contrib.auth import authenticate, get_user_model
from django.conf import settings
from django.db import transaction
from django.db.models import Q

from authentication import serializers as auth_serializers
from authentication import models as auth_models
from shared_functions import service_responses, time_functions, authsystemuser

service_response = service_responses.ServiceResponseManager()
time_function = time_functions
oauth2user = authsystemuser.ApplicationUser()

application_label = 'authentication'
log = logging.getLogger(__name__)


class CitizenAccountViewSet(viewsets.ViewSet):
    permission_classes = (permissions.AllowAny, )

    @action(
        methods=['POST'],
        detail=False,
        url_name='register-user',
        url_path='register-user'
    )
    def public_register(self, request):
        payload = request.data
        serializer = auth_serializers.RegisterUserSerializer(
            data=payload, many=False)
        if serializer.is_valid(raise_exception=True):
            phone_number = serializer.data.get('phone_number')
            email = serializer.data.get('email')
            user_name = serializer.data.get('name')
            gender = serializer.data.get('gender')
            hashed_password = serializer.validated_data.get('hashed_password')

            with transaction.atomic():
                user_query = get_user_model().objects.filter(Q(phone_number=phone_number))
                if user_query.exists():
                    user_details = user_query.first()
                    if user_details.is_active:
                        return Response(
                            {
                                "details": "Phone number already registered. Kindly login.",
                                "phone_number": phone_number,
                                "PHONE_VERIFICATION": True,
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    return Response(
                        {
                            "details": "Phone number already registered. Awaiting verification",
                            "phone_number": phone_number,
                            "PHONE_VERIFICATION": False
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                try:
                    user_type_instance = auth_models.UserCategoryType \
                        .objects.get(name='PUBLICUSER')
                except Exception as e:
                    log.error(e)
                    return Response(
                        {'details': "Failed to register. Try again later"},
                        status=status.HTTP_400_BAD_REQUEST)

                user_payload = {
                    "phone_number": phone_number,
                    "email": email,
                    "usertype": user_type_instance,
                    "is_staff": False,
                    "is_admin": False,
                    "is_superuser": False,
                    "enable_phone_notification": True,
                    "enable_email_notification": True,
                }

                new_user = get_user_model().objects.create(**user_payload)
                try:
                    public_group = Group.objects.get(name="PUBLIC")
                    public_group.user_set.add(new_user)
                    new_user.primary_role = public_group.id
                    public_group.save()
                except Exception as e:
                    log.error(e)
                    transaction.set_rollback(True)
                    return Response({"details": "Failed to register. Try again later"})

                oauth2user.create_application_user(new_user, email)

                # create profile instance
                try:
                    profile_payload = {
                        "userid": new_user,
                        "fullname": user_name,
                        "gender": gender,
                        'is_passwordverified': True
                    }

                    auth_models.PublicUserProfile.objects.create(
                        **profile_payload)
                except Exception as e:
                    log.error(e)
                    transaction.set_rollback(True)
                    return Response(
                        {"details": "Failed to update profile. Try again later"},
                        status=status.HTTP_400_BAD_REQUEST)

                new_user.is_active = True
                new_user.password = hashed_password
                new_user.save()

                # send otp for verification
                otp_payload = {
                    "user": str(new_user.id),
                    "send_to": phone_number,
                    "mode": "sms",
                    "module": "REGISTRATION_SMS_VERIFICATION",
                    "expiry_time": settings.REGISTRATION_OTP_EXPIRY_TIME
                }
                otp_generated, otp_response = service_response.generate_otp_code(
                    otp_payload)
                if not otp_generated:
                    log.error(otp_response)
                    transaction.set_rollback(True)
                    return Response(
                        {"details": "Failed to register. Try again later"},
                        status=status.HTTP_400_BAD_REQUEST)

                otp_code = otp_response['code']

                # send sms
                sms_payload = {
                    "phone": phone_number,
                    "message": f"Your registration verification code is: {otp_code}"
                }
                # sending_sms = service_response.send_bulk_sms(sms_payload)
                # if not sending_sms:
                #     return Response(
                #         {"details": "Failed to send sms. Check your phone number"},
                #         status=status.HTTP_401_UNAUTHORIZED)

                if not settings.DEBUG:
                    otp_code = None
                return Response(
                    {
                        "details": "Account Created. Kindly proceed to verify phone number.",
                        "otp_code": otp_code
                    })
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    @action(
        methods=['POST'],
        detail=False,
        url_name='resend-otp',
        url_path='resend-otp'
    )
    def resend_otp(self, request):
        payload = request.data
        serializer = auth_serializers.ResendOtpSerializer(
            data=payload, many=False)
        if serializer.is_valid(raise_exception=True):
            phone_number = serializer.data.get('phone_number')
            module = serializer.data.get('module')
            try:
                user_details = get_user_model().objects.get(phone_number=phone_number)
            except Exception as e:
                log.error(e)
                return Response({"details": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            try:
                profile_details = user_details.public_user
            except Exception as e:
                log.error(e)
                return Response(
                    {'details': "Invalid Profile Details"},
                    status=status.HTTP_404_NOT_FOUND)

            module_code = "LOGIN"
            if module == "REGISTER":
                if profile_details.is_phoneverified:
                    return Response(
                        {"details": "Phone number is already verified"},
                        status=status.HTTP_400_BAD_REQUEST)

                module_code = 'REGISTRATION_SMS_VERIFICATION'

            # send otp for verification
            otp_payload = {
                "user": str(user_details.id),
                "send_to": phone_number,
                "mode": "sms",
                "module": module_code,
                "expiry_time": settings.REGISTRATION_OTP_EXPIRY_TIME
            }
            otp_generated, otp_response = service_response.generate_otp_code(
                otp_payload)
            if not otp_generated:
                log.error(otp_response)
                transaction.set_rollback(True)
                return Response(
                    {"details": "Failed to send verification code. Try again later"},
                    status=status.HTTP_400_BAD_REQUEST)

            otp_code = otp_response['code']
            # sending sms
            sms_payload = {
                "phone": phone_number,
                "message": f"Your verification code is: {otp_code}"
            }

            sending_sms = service_response.send_bulk_sms(sms_payload)
            if not sending_sms:
                return Response(
                    {"details": "Failed to send sms. Check your phone number."},
                    status=status.HTTP_401_UNAUTHORIZED)

            if not settings.DEBUG:
                otp_code = None
            return Response(
                {
                    "details": "Verification Code sent successfully",
                    "otp_code": otp_code
                })
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    @action(
        methods=['POST'],
        detail=False,
        url_name='verify-otp',
        url_path='verify-otp'
    )
    def verify_otp(self, request):
        payload = request.data
        serializer = auth_serializers.VerifyLoginOtpSerializer(data=payload)
        if serializer.is_valid(raise_exception=True):
            phone_number = serializer.data.get("phone_number")
            password = serializer.data.get("password")
            otp_code = serializer.data.get("otp_code")

            try:
                user_details = get_user_model().objects.get(phone_number=phone_number)
            except Exception as e:
                log.error(e)
                return Response(
                    {"details": "User not found"},
                    status=status.HTTP_404_NOT_FOUND)

            otp_params = {
                "user_id": str(user_details.id),
                "otp_code": otp_code,
                "module": "REGISTRATION_SMS_VERIFICATION"
            }

            validated_otp, response_inf = service_response.verify_otp_code(
                otp_params)
            if not validated_otp:
                return Response(
                    {"details": response_inf['details']},
                    status=status.HTTP_400_BAD_REQUEST)

            user = authenticate(phone_number=phone_number, password=password)
            if not bool(user):
                return Response(
                    {"details": "Invalid phone number or password"},
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
                    'username': phone_number,
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

            profile_details = user_details.public_user
            profile_details.is_phoneverified = True
            profile_details.save()

            return Response({"details": user_info}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
