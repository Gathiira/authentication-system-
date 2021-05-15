from django.core.mail import send_mail, send_mass_mail


def broad_cast_system_notification(subject, message, receiver):
    try:
        response = send_mail(subject=subject, message=message, from_email=None,
                             recipient_list=receiver, fail_silently=False)
        if response > 0:
            return True, response
        return False, response
    except Exception as e:
        print(e)
        return False, 0


def broad_cast_mass_system_notification(subject, message, receiver):
    try:
        message1 = (subject, message, None, receiver)
        response = send_mass_mail((message1, ), fail_silently=False)
        if response > 0:
            return True, response
        return False, response
    except Exception as e:
        print(e)
        return False, 0
