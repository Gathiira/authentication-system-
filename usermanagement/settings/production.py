from .base import *
from dotenv import load_dotenv
load_dotenv()
if os.environ.get('DEBUG_MODE') == 'True':
    DEBUG = True
elif os.environ.get('DEBUG_MODE') == 'False':
    DEBUG = False


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': os.getenv('DATABASE_NAME'),
#         'USER': os.environ.get('DATABASE_USERNAME'),
#         'PASSWORD': os.environ.get('DATABASE_PASSWORD'),
#         'OPTIONS': {
#             'options': '-c search_path={}'.format(os.environ.get('DATABASE_SCHEMA'))
#         },
#         'HOST': str(os.environ.get('DATABASE_HOST')),
#         'PORT': int(os.environ.get('DATABASE_PORT')),
#         'TEST': {
#             'ENGINE': 'django.db.backends.postgresql_psycopg2',
#             'NAME':  os.environ.get('DATABASE_NAME'),
#             'USER': os.environ.get('DATABASE_USERNAME'),
#             'PASSWORD': os.environ.get('DATABASE_PASSWORD'),
#             'OPTIONS': {
#                 'options': '-c search_path={}'.format(os.environ.get('DATABASE_SCHEMA'))
#             },

#         },
#         'ATOMIC_REQUESTS': True

#     }
# }


prod_db = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(prod_db)

OTP_EXPIRY_TIME = int(os.getenv('OTP_EXPIRY_TIME'))
OTP_PASSWORD_RESET_TIME = int(os.getenv('OTP_PASSWORD_RESET_TIME'))


INVITATION_LINK_EXPIRY = int(os.getenv('INVITATION_LINK_EXPIRY'))
DATA_UPLOAD_MAX_NUMBER_FIELDS = int(os.getenv('DATA_UPLOAD_MAX_NUMBER_FIELDS'))
if os.environ.get('TRANSFERPROTOCOL') is None:
    os.environ.setdefault('TRANSFERPROTOCOL', 'https')

OTP_REGISTRATION_VERIFICATION = os.environ.get('OTP_REGISTRATION_VERIFICATION')
MINIMUM_PASSWORD_LENGTH = int(os.environ.get('MINIMUM_PASSWORD_LENGTH'))


SERVICE_URLS = {
    'acl_service': os.environ.get('TRANSFER_PROTOCOL') + '://' + os.environ.get('ACL_SERVICE') + os.environ.get('API_VERSION'),
    'shared_service': os.environ.get('TRANSFER_PROTOCOL') + '://' + os.environ.get('SHARED_SERVICE') + os.environ.get('API_VERSION'),
}


#  email settings
EMAIL_USE_TLS = True
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = os.environ.get('EMAIL_PORT')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

# admins
SERVER_EMAIL = 'root@localhost.com'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

ADMINS = ()
if os.environ.get('DEBUG_MODE') == 'False':
    ADMINS = (
        ('Joseph', 'kazimoja.email@gmail.com'),
    )

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_FILE_PATH = os.path.join(BASE_DIR, '../logs/app-messages')


SMS_USERNAME = os.environ.get('SMS_USERNAME')
SMS_API_KEY = os.environ.get('SMS_API_KEY')
SMS_SENDERID = os.environ.get('SMS_SENDERID')
