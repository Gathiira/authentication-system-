import logging
from django.conf import settings
import requests

log = logging.getLogger(__name__)


class ServiceResponseManager:
    def __init__(self):
        self.service_urls = settings.SERVICE_URLS
        self.acl_service = self.service_urls['acl_service']
        self.shared_service = self.service_urls['shared_service']

    def get_current_server_url(self, request):
        host_server = request.get_host()
        request_is_secure = request.is_secure()
        host_url = None
        if request_is_secure:
            host_url = 'https://' + host_server
        else:
            host_url = 'http://' + host_server
        return host_url

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

    def verify_otp_code(self, payload):
        url = self.acl_service + 'mfa/otp/verify-otp-code'
        try:
            response = requests.post(url, json=payload)

            if response.status_code == 200:
                return True, response.json()
            else:
                log.error(response.text)
                return False, response.json()
        except Exception as e:
            log.error(e)
            return False, "Failed to verify otp code"

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

    def send_bulk_sms(self, payload):
        url = self.shared_service + 'sms/createsmsrequest'
        try:
            sms_payload = [{
                "phone": payload['phone'][1:],
                "message": payload['message']
            }]
            response = requests.post(url=url, json=sms_payload)
            if response.status_code == 200:
                return True
            log.error(response.text)
            return False
        except Exception as e:
            log.error(e)
            return False
