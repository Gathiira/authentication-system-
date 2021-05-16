import logging
from django.contrib.auth.models import Group
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action

from django.contrib.auth import authenticate, get_user_model
from django.apps import apps as system_apps
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from rest_framework.utils.serializer_helpers import ReturnList

from authentication import serializers as auth_serializers
from authentication import models as auth_models
from shared_functions import service_responses, time_functions, authsystemuser

service_response = service_responses.ServiceResponseManager()
time_function = time_functions
oauth2user = authsystemuser.ApplicationUser()

application_label = 'authentication'
log = logging.getLogger(__name__)


class CitizenAccountViewSet(viewsets.GenericViewSet):
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
            username = serializer.data.get('username')
            email = serializer.data.get('email')
            phone_number = serializer.data.get('phone_number')
            f_name = serializer.data.get('f_name')
            m_name = serializer.data.get('m_name')
            l_name = serializer.data.get('l_name')
            gender = serializer.data.get('gender')
            hashed_password = serializer.validated_data.get('hashed_password')
            location = serializer.data.get('location')

            with transaction.atomic():
                user_query = get_user_model().objects.filter(
                    Q(email=email) | Q(username=username))
                if user_query.exists():
                    user_details = user_query.first()
                    if user_details.is_active:
                        return Response(
                            {
                                "details": "User already registered. Kindly login to continue",
                                "email": email,
                                "EMAIL_VERIFICATION": True,
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    return Response(
                        {
                            "details": "User already registered. Awaiting email verification",
                            "email": email,
                            "EMAIL_VERIFICATION": False
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
                    "username": username,
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
                        "phonenum": phone_number,
                        "firstname": f_name,
                        "middlename": m_name,
                        "lastname": l_name,
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

                # new_user.is_active = True
                new_user.password = hashed_password
                new_user.save(update_fields=['is_active', 'password'])

                # send otp for verification
                otp_payload = {
                    "user": str(new_user.id),
                    "send_to": email,
                    "mode": "email",
                    "module": "REGISTRATION_EMAIL_VERIFICATION",
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
                notification_payload = {
                    "subject": "VERIFICATION CODE",
                    "recipients": [email],
                    "message": f"Your registration verification code is {otp_code}",
                }
                #  send email
                sending_mail = service_response.send_email(
                    notification_payload)
                if not sending_mail:
                    return Response(
                        {"details": "Failed to send mail. Check your mail or internet connection"},
                        status=status.HTTP_401_UNAUTHORIZED)

                if not settings.DEBUG:
                    otp_code = None
                return Response(
                    {
                        "details": "Account Created. Kindly proceed to verify email.",
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
            email = serializer.data.get('email')
            module = serializer.data.get('module')
            try:
                user_details = get_user_model().objects.get(email=email)
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
                if profile_details.is_emailverified:
                    return Response(
                        {"details": "Email is already verified"},
                        status=status.HTTP_400_BAD_REQUEST)

                module_code = 'REGISTRATION_EMAIL_VERIFICATION'

            # send otp for verification
            otp_payload = {
                "user": str(user_details.id),
                "send_to": email,
                "mode": "email",
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
            notification_payload = {
                "subject": "RESENT VERIFICATION CODE",
                "recipients": [email],
                "message": f"Your new resent verification code is {otp_code}",
            }
            #  send email
            sending_mail = service_response.send_email(
                notification_payload)
            if not sending_mail:
                return Response(
                    {"details": "Failed to send mail. Check your mail or internet connection"},
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
        serializer = auth_serializers.VerifyOtpSerializer(
            data=payload, many=False)
        if serializer.is_valid(raise_exception=True):
            email = serializer.data.get('email')
            otp_code = serializer.data.get('otp_code')
            module = serializer.data.get('module')
            try:
                user_details = get_user_model().objects.get(email=email)
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
                if profile_details.is_emailverified:
                    return Response(
                        {"details": "Email is already verified"},
                        status=status.HTTP_400_BAD_REQUEST)

                module_code = 'REGISTRATION_EMAIL_VERIFICATION'

            verification_payload = {
                "user_id": str(user_details.id),
                "otp_code": otp_code,
                "module": module_code
            }
            validate_otp, messagedata = service_response.verify_otp_code(
                verification_payload)
            if not validate_otp:
                return Response(
                    {"details": messagedata['details']},
                    status=status.HTTP_400_BAD_REQUEST)

            if module == "REGISTER":
                user_details.is_active = True
                user_details.save(update_fields=['is_active'])

                profile_details.is_emailverified = True
                profile_details.save(update_fields=['is_emailverified'])

                return Response(
                    {'details': 'Email successfully verified. Kindly proceed to login'},
                    status=status.HTTP_200_OK)

            return Response(
                {'details': 'Otp Verified. Kindly proceed to login'},
                status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
