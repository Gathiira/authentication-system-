import logging
from django.conf import settings
from django.db import transaction
from rest_framework import status, viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action


from notification import models as notification_models
from notification import serializers as notification_serializers

from notification import email_sender


log = logging.getLogger(__name__)


class EmailViewSet(viewsets.GenericViewSet):
    permission_classes = (permissions.AllowAny, )

    @action(
        methods=['POST'],
        detail=False,
        url_path='send-email',
        url_name='send-email'
    )
    def send_email(self, request):
        payload = request.data
        serializer = notification_serializers.EmailSerializer(
            data=payload, many=False)

        if serializer.is_valid(raise_exception=True):
            with transaction.atomic():
                subject = serializer.data.get('subject')
                message = serializer.data.get('message')
                recipients = serializer.data.get('recipients')

                email_payload = {
                    "sender": "SYSTEM",
                    "subject": subject,
                    "message": message,
                    "status": "PENDING"
                }

                created_mail = notification_models.EmailNotification(
                    **email_payload)
                created_mail.save()

                for recipient in recipients:
                    rec_payload = {
                        "recipient": recipient,
                        "email_request": created_mail
                    }

                    rec_instance = notification_models.EmailRecipients(
                        **rec_payload)
                    rec_instance.save()

                sending_email, response = email_sender.broad_cast_mass_system_notification(
                    subject, message, recipients)
                if sending_email <= 0:
                    log.error(f"{response} sent email")

                log.info(f'{response} sent mails')

                email_details = notification_serializers.EmailDetailSerializer(
                    created_mail, many=False).data

                return Response(email_details)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
