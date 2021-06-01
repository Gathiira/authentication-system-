from rest_framework import serializers


class SMSSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=100)
    message = serializers.CharField(max_length=2000)
