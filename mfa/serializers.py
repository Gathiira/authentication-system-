from rest_framework import serializers

from mfa import models as mfa_models


class OTPSerializer(serializers.Serializer):
    user = serializers.CharField()
    send_to = serializers.CharField()
    module = serializers.CharField()
    expiry_time = serializers.IntegerField()


class OtpCodeDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = mfa_models.CodeVerification
        exclude = ('user', )


class VerifyOTPSerializer(serializers.Serializer):
    otp_code = serializers.CharField()
    user_id = serializers.CharField()
    module = serializers.CharField()
