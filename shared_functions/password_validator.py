from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings
import random
import string
import re


regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]')


class PasswordManager:
    def __init__(self) -> None:
        pass

    def generate_hashed_password(self, password):
        hashed_pass = make_password(password)
        return str(hashed_pass)

    def validate_password_confirmation(self, password, confirm_pass):
        if password != confirm_pass:
            return {
                "status": False,
                "error": "Password must be similar"
            }
        return {
            "status": True
        }

    def validate_password_security(self, user_password):
        password_min_length = settings.MINIMUM_PASSWORD_LENGTH
        if len(user_password) < password_min_length:
            return {
                "status": False,
                "error": f"Password must be atleast {password_min_length} characters"
            }
        elif not any(char.isdigit() for char in user_password):
            return {
                "status": False,
                "error": 'Password must contain at least 1 digit'
            }
        elif not any(char.isalpha() for char in user_password):
            return {
                "status": False,
                "error": 'Password must contain at least 1 letter'
            }

        elif(regex.search(user_password) == None):
            return {
                "status": False,
                "error": 'Password must contain at least 1 special character'
            }
        else:
            return {
                "status": True,
            }

    def check_old_password(self, new_password, existing_password):
        is_old_password = check_password(new_password, existing_password)
        if is_old_password:
            return True
        else:
            return False

    def generate_random_password(self):
        letters_and_digits = string.ascii_letters + string.digits
        result_str = ''.join((random.choice(letters_and_digits)
                              for i in range(settings.MINIMUM_PASSWORD_LENGTH)))
        return result_str
