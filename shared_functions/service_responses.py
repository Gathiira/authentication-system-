import logging
from django.conf import settings
import requests

log = logging.getLogger(__name__)


class ServiceResponseManager:
    def __init__(self):
        self.service_urls = settings.SERVICE_URLS
        self.acl_service = self.service_urls['acl_service']

    def get_resource_server(self):
        url = self.acl_service + 'o/token/'
        return url

    def generate_otp_code(self, payload):
        url = self.acl_service + 'mfa/otp/generate-otp-code'
        try:
            response = requests.post(url, json=payload)

            if response.status_code == 200:
                return True, response.json()
            else:
                log.error(response.text)
                return False, response.json()
        except Exception as e:
            log.error(e)
            return False, "Failed to generate otp code"

    def send_email(self, payload):
        url = self.acl_service + "notification/email/send-email"
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                return response.json()
            else:
                message = response.json()
                log.error(message)
                return False
        except Exception as e:
            log.error(e)
            return False
