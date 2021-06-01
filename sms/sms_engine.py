import africastalking


class SMSEngine:
    def __init__(self):
        # Set your app credentials
        self.username = "sandbox"
        self.api_key = "a64126ccf815aaa09fb303cd5c579815fca6de74a1e02cca428d490391a82678"

        # Initialize the SDK
        africastalking.initialize(self.username, self.api_key)

        # Get the SMS service
        self.sms = africastalking.SMS

    def sendSMS(self, recipients, message):
        # Set your shortCode or senderId
        sender = "SHARERIDE"
        try:
            # Thats it, hit send and we'll take care of the rest.
            response = self.sms.send(message, recipients, sender)
            return response
        except Exception as e:
            return f'Encountered an error while sending: {str(e)}'
