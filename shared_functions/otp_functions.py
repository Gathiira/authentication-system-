import random
from shared_functions import time_functions
from mfa import models as mfa_models


time_function = time_functions


def generate_random_code():
    otp_code = ""
    for i in range(6):
        otp_code += str(random.randint(1, 9))
    return otp_code


def generate_otp_code():
    otp_code = generate_random_code()
    otp_query = mfa_models.CodeVerification.objects.filter(code=otp_code)
    if otp_query.exists():
        return generate_otp_code()
    return otp_code


def verify_otp_code(otp, userid, module):
    code_query = mfa_models.CodeVerification.objects.filter(
        code=otp, user=userid, module=module).exclude(status="REVOKED")
    if code_query.exists():
        if code_query.count() == 1:
            otp_details = code_query.first()
            current_time = time_function.get_current_timestamp()
            expiry_time = otp_details.expiry_time

            code_is_expired = time_function.check_date_expiry(
                str(current_time), str(expiry_time))
            if code_is_expired:
                otp_details.status = "REVOKED"
                otp_details.save(update_fields=['status'])
                return False, "The code is expired. Try again"

            otp_details.status = "REVOKED"
            otp_details.save(update_fields=['status'])
            return True, "Code is ok"
        return False, "Invalid Otp code"
    return False, "Invalid Otp code"
