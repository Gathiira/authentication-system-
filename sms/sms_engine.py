import africastalking
from django.conf import settings


class SMSEngine:
    def __init__(self):
        # Set your app credentials
        self.username = settings.SMS_USERNAME
        self.api_key = settings.SMS_API_KEY

        # Initialize the SDK
        africastalking.initialize(self.username, self.api_key)

        # Get the SMS service
        self.sms = africastalking.SMS

    def sendSMS(self, recipients, message):
        # Set your shortCode or senderId
        sender = settings.SMS_SENDERID
        try:
            # Thats it, hit send and we'll take care of the rest.
            response = self.sms.send(message, recipients)
            return response
        except Exception as e:
            return f'Encountered an error while sending: {str(e)}'
