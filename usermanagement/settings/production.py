from .base import *
from dotenv import load_dotenv
load_dotenv()
if os.environ.get('DEBUG_MODE') == 'True':
    DEBUG = True
elif os.environ.get('DEBUG_MODE') == 'False':
    DEBUG = False


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('DATABASE_NAME'),
        'USER': os.environ.get('DATABASE_USERNAME'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD'),
        'OPTIONS': {
            'options': '-c search_path={}'.format(os.environ.get('DATABASE_SCHEMA'))
        },
        'HOST': str(os.environ.get('DATABASE_HOST')),
        'PORT': int(os.environ.get('DATABASE_PORT')),
        'TEST': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME':  os.environ.get('DATABASE_NAME'),
            'USER': os.environ.get('DATABASE_USERNAME'),
            'PASSWORD': os.environ.get('DATABASE_PASSWORD'),
            'OPTIONS': {
                'options': '-c search_path={}'.format(os.environ.get('DATABASE_SCHEMA'))
            },

        },
        'ATOMIC_REQUESTS': True

    }
}

OTP_EXPIRY_TIME = int(os.getenv('OTP_EXPIRY_TIME'))
OTP_PASSWORD_RESET_TIME = int(os.getenv('OTP_PASSWORD_RESET_TIME'))


INVITATION_LINK_EXPIRY = int(os.getenv('INVITATION_LINK_EXPIRY'))
DATA_UPLOAD_MAX_NUMBER_FIELDS = int(os.getenv('DATA_UPLOAD_MAX_NUMBER_FIELDS'))
if os.environ.get('TRANSFERPROTOCOL') is None:
    os.environ.setdefault('TRANSFERPROTOCOL', 'https')

OTP_REGISTRATION_VERIFICATION = os.environ.get('OTP_REGISTRATION_VERIFICATION')
MINIMUM_PASSWORD_LENGTH = int(os.environ.get('MINIMUM_PASSWORD_LENGTH'))
