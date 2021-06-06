from shared_functions import service_responses
import requests
from django.core.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from oauth2_provider.models import get_application_model

service_response = service_responses.ServiceResponseManager()


class SystemServiceManager:
    def __init__(self):
        pass

    def logout_user(self, request, token, user_id):
        try:
            user_details = get_application_model().objects.get(user_id=user_id)
        except (ValidationError, ObjectDoesNotExist):
            return False, "User does not exist"
        request_url = service_response.get_current_server_url(request)
        revoke_url = request_url + '/o/revoke_token/'
        payload_data = {
            'token': token,
            'client_id': user_details.client_id,
            'client_secret': user_details.client_secret,
        }
        response = requests.post(revoke_url, data=payload_data)
        if response.status_code == 200:
            return True, "Logout Successful"
        return False, "Failed to log you out"
