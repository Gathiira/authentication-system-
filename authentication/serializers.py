from rest_framework import serializers
from django.core.validators import RegexValidator

from shared_functions import password_validator

password_checker = password_validator.PasswordManager()


phone_regex = RegexValidator(
    regex=r'^\+?254?\d{10,12}$',
    message="Phone number must be entered in the format: '+254123456789'. Up to 12 digits allowed.")


class GenericEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


MODULE_CHOICES = [
    ("LOGIN", 'LOGIN'),
    ("REGISTER", 'REGISTER'),
]


class ResendOtpSerializer(GenericEmailSerializer):
    module = serializers.ChoiceField(choices=MODULE_CHOICES)


class VerifyOtpSerializer(ResendOtpSerializer):
    otp_code = serializers.CharField()


class LoginSerializer(GenericEmailSerializer):
    password = serializers.CharField()
    usertype = serializers.CharField()


GENDER = [
    ("MALE", 'MALE'),
    ("FEMALE", 'FEMALE'),
]


class RegisterUserSerializer(GenericEmailSerializer):
    username = serializers.CharField(required=True)
    phone_number = serializers.CharField(
        required=True, validators=[phone_regex])
    f_name = serializers.CharField(required=True)
    m_name = serializers.CharField(required=True)
    l_name = serializers.CharField(required=True)
    gender = serializers.ChoiceField(choices=GENDER)
    password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)
    location = serializers.CharField(required=True)

    def validate(self, obj):
        pass1 = obj['password']
        pass2 = obj['confirm_password']

        pass_length_check = password_checker.validate_password_confirmation(
            pass1, pass2)

        if not pass_length_check['status']:
            raise serializers.ValidationError(pass_length_check['error'])

        # validating the password
        password_response = password_checker.validate_password_security(pass1)

        if not password_response['status']:
            raise serializers.ValidationError(password_response['error'])

        obj.update(
            {
                "hashed_password": password_checker.generate_hashed_password(
                    pass1)
            }
        )

        return obj
