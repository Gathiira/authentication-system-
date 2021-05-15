from rest_framework import serializers

from notification import models as notification_models


class EmailSerializer(serializers.Serializer):
    recipients = serializers.ListField(required=True)
    message = serializers.CharField()
    subject = serializers.CharField()


class EmailRecipientDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = notification_models.EmailRecipients
        fields = ['recipient']


class EmailDetailSerializer(serializers.ModelSerializer):
    recipients = serializers.SerializerMethodField('get_recipients')

    class Meta:
        model = notification_models.EmailNotification
        fields = ["id", 'sender', 'subject', 'message', 'status', 'recipients']

    def get_recipients(self, obj):
        recipients = obj.email_repients.all()
        details = EmailRecipientDetailSerializer(recipients, many=True).data
        all_recipients = []
        for data in details:
            all_recipients.append(data['recipient'])
        return all_recipients
