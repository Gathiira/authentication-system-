from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import SMSSerializer
from sms.sms_engine import SMSEngine
smsbroadcast = SMSEngine()


class QueueSMSView(APIView):
    def post(self, request):
        payload = request.data
        serializer = SMSSerializer(data=payload, many=True)
        serializer.is_valid(raise_exception=True)
        phone_payload = []
        for data in payload:
            phoneno = data['phone']
            message = data['message']
            newphoneno = "+254" + str(phoneno)
            phone_payload.append(newphoneno)
        else:
            sendsms = smsbroadcast.sendSMS(phone_payload, message)
            return Response(
                {'details': 'Vendor2 Message BroadCast Successful'},
                status=status.HTTP_200_OK)
