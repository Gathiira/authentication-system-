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

from authentication import serializers as auth_serializers
from authentication import models as auth_models
from shared_functions import service_responses, time_functions, authsystemuser

service_response = service_responses.ServiceResponseManager()
time_function = time_functions
oauth2user = authsystemuser.ApplicationUser()

application_label = 'authentication'
log = logging.getLogger(__name__)


class CitizenAccountViewSet(viewsets.GenericViewSet):

    @action(
        methods=['POST'],
        detail=False,
        url_name='email-validate',
        url_path='email-validate'
    )
    def email_validate(self, request):
        payload = request.data
        serializer = auth_serializers.EmailSerializer(data=payload, many=False)
        if serializer.is_valid(raise_exception=True):
            username = serializer.data.get('username')
            email = serializer.data.get('email')
            with transaction.atomic():
                user_query = get_user_model().objects.filter(
                    Q(email=email) | Q(username=username))
                if user_query.exists():
                    user_details = user_query.first()
                    try:
                        user_details.public_user
                    except:
                        return Response({"details": "User already registered. Kindly complete with the profile"})

                    return Response({"details": "User already registered. Kindly login to continue"})

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
                    "subject": "EMAIL VERIFICATION CODE",
                    "recipients": [email],
                    "message": f"Your login verification code is {otp_code}",
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
                        "details": "Account Created. Kindly proceed to verify details using the code sent to the provided email.",
                        "otp_code": otp_code
                    })
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
