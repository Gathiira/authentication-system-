from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action

from shared_functions import time_functions, otp_functions


from mfa import models as mfa_models
from mfa import serializers as mfa_serializers

time_function = time_functions
otp_function = otp_functions


class OtpView(viewsets.ViewSet):
    permission_classes = (permissions.AllowAny,)

    @action(methods=['POST'], detail=False, url_path="generate-otp-code", url_name="generate-otp-code")
    def generate_otp_code(self, request):
        payload = request.data
        serializer = mfa_serializers.OTPSerializer(data=payload, many=False)
        if serializer.is_valid(raise_exception=True):
            user_id = serializer.data.get('user')
            send_to = serializer.data.get('send_to')
            # mode = serializer.data.get('mode')
            module = serializer.data.get('module')
            expiry_time = serializer.data.get('expiry_time')

            generation_time = time_function.get_current_timestamp()
            new_expiry_time = time_function.add_time_to_date(
                'seconds', generation_time, int(expiry_time))
            new_code = otp_function.generate_otp_code()

            otp_payload = {
                "user": user_id,
                "send_to": send_to,
                "creation_date": generation_time,
                "expiry_time": new_expiry_time,
                "code": new_code,
                "status": "PENDING",
                "module": module
            }
            code_instance = mfa_models.CodeVerification(**otp_payload)
            code_instance.save()
            code_details = mfa_serializers.OtpCodeDetailSerializer(
                code_instance, many=False).data
            return Response(code_details)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'], detail=False, url_path="verify-otp-code", url_name="verify-otp-code")
    def verify_otp_code(self, request):
        payload = request.data
        serializer = mfa_serializers.VerifyOTPSerializer(
            data=payload, many=False)
        if serializer.is_valid(raise_exception=True):
            otp_code = serializer.data.get("otp_code")
            user = serializer.data.get("user_id")
            module = serializer.data.get("module")

            is_verified, message = otp_function.verify_otp_code(
                otp_code, user, module)
            if is_verified:
                return Response({"details": "Opt Verification successful"})
            return Response({"details": message}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
