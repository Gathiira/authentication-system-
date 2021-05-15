from rest_framework import serializers

from mfa import models as mfa_models


class OTPSerializer(serializers.ModelSerializer):

    class Meta:
        model = mfa_models.CodeVerification
        fields = ['user', 'send_to', 'mode', 'expiry_time']


class OtpCodeDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = mfa_models.CodeVerification
        exclude = ('user', )


class VerifyOTPSerializer(serializers.Serializer):
    otp_code = serializers.CharField()
    user_id = serializers.CharField()
    module = serializers.CharField()
