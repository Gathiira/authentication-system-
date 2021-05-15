from django.db import transaction
from rest_framework.exceptions import APIException
from oauth2_provider.generators import generate_client_id, generate_client_secret
from oauth2_provider.models import get_application_model


class ApplicationUser:

    def __init__(self) -> None:
        pass

    def create_application_user(self, user, email):
        try:
            with transaction.atomic():
                new_client_id = generate_client_id()
                new_client_secret = generate_client_secret()

                application_data = {
                    "user": user,
                    "client_id": new_client_id,
                    "client_secret": new_client_secret,
                    "name": email,
                    "skip_authorization": False,
                    "redirect_uris": "",
                    "client_type": 'confidential',
                    "authorization_grant_type": 'password'
                }

                new_application = get_application_model().objects.create(**application_data)
                new_application.save()

                if new_application:
                    return True
                return False
        except Exception as e:
            raise APIException({e})
