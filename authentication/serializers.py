from rest_framework import serializers
from django.core.validators import RegexValidator

from shared_functions import password_validator, service_responses

from authentication import models as auth_models

password_checker = password_validator.PasswordManager()
service_response = service_responses.ServiceResponseManager()


phone_regex = RegexValidator(
    regex=r'^\+?0?\d{9,9}$',
    message="Phone number must be entered in the format: '0712345678'. Up to 10 digits allowed.")


class GenericPhoneNumberSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        required=True, validators=[phone_regex])


MODULE_CHOICES = [
    ("LOGIN", 'LOGIN'),
    ("REGISTER", 'REGISTER'),
]


class ResendOtpSerializer(GenericPhoneNumberSerializer):
    module = serializers.ChoiceField(choices=MODULE_CHOICES)


class VerifyLoginOtpSerializer(GenericPhoneNumberSerializer):
    otp_code = serializers.CharField()
    password = serializers.CharField()


class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(required=True)


class LoginSerializer(GenericPhoneNumberSerializer):
    password = serializers.CharField()
    usertype = serializers.CharField()


GENDER = [
    ("MALE", 'MALE'),
    ("FEMALE", 'FEMALE'),
]


class RegisterUserSerializer(GenericPhoneNumberSerializer):
    email = serializers.EmailField(required=True)
    name = serializers.CharField(required=True)
    gender = serializers.ChoiceField(choices=GENDER)
    password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

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


class GetUserDetailSerializer(serializers.Serializer):
    userid = serializers.CharField(required=True)


class UserProfilePhotoSerializer(serializers.ModelSerializer):
    profile_photo = serializers.SerializerMethodField("get_user_profile_photo")

    class Meta:
        model = auth_models.User
        fields = ["profile_photo"]

    def get_user_profile_photo(self, obj):
        photo_id = obj.profile_photo
        photo_details = service_response.get_document_details(
            photo_id)
        if photo_details is False:
            user_photo_url = ""
        else:
            user_photo_url = photo_details['file']
        return user_photo_url
