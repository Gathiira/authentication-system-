import os
import django_heroku
import dj_database_url
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = os.environ.get("SECRET_KEY")
ALLOWED_HOSTS = os.environ.get("APPLICATION_ALLOWED_HOSTS").split(",")
INSTALLED_APPS = [
    'authentication',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'drf_yasg',
    'oauth2_provider',
    'logging_middleware',
    'mfa',
    'notification',
]

MIDDLEWARE = [

    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'logging_middleware.middlewares.DjangoLoggingMiddleware'
]

DJANGO_LOGGING_MIDDLEWARE = {
    'DEFAULT_FORMAT': False,
    'MESSAGE_FORMAT': "<b><green>{time}</green> <cyan>{message}</cyan></b>"
}
ROOT_URLCONF = 'usermanagement.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'usermanagement.wsgi.application'
'''
Overriding default authentication class
'''
REST_FRAMEWORK = {
    "NON_FIELD_ERRORS_KEY": "details",
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],

    'DEFAULT_AUTHENTICATION_CLASSES': (
        'authentication.tokenbackend.SystemAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PAGINATION_CLASS':
    'shared_functions.pagination_functions.StandardResultsSetPagination'
}
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Nairobi'

USE_I18N = True

USE_L10N = True

USE_TZ = False

AUTH_USER_MODEL = 'authentication.User'

STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, "media")


FIELD_ENCRYPTION_KEY = 'fiflN_F353HczfcXxxniJSzpvYR_C4-IIuXuNoQYjdY='
ACCESS_TOKEN_EXPIRY_TIME = 2
REFRESH_TOKEN_EXPIRY_TIME = 5
TOKEN_SECRET_KEY = os.environ.get('SECRET_KEY')
CORS_ORIGIN_ALLOW_ALL = True
if os.environ.get('CORS_ALLOW_ALL') == 'True':
    CORS_MODE = True
elif os.environ.get('CORS_ALLOW_ALL') == 'False':
    CORS_MODE = False

CORS_ORIGIN_ALLOW_ALL = CORS_MODE
CORS_ORIGIN_WHITELIST = os.environ.get("CORS_WHITELIST").split(",")
CORS_ORIGIN_REGEX_WHITELIST = os.environ.get("CORS_WHITELIST").split(",")
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'AUTH',
    'JWTAUTH',
    'AUTHORIZATION',
    'HTTP_AUTHORIZATION',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

OAUTH2_PROVIDER = {
    'ACCESS_TOKEN_EXPIRE_SECONDS': int(os.environ.get('ACCESS_TOKEN_EXPIRY')),
    'OAUTH_SINGLE_ACCESS_TOKEN': True,
    'OAUTH_DELETE_EXPIRED': True,
    'ROTATE_REFRESH_TOKEN': True,
}
ACCESS_TOKEN_EXPIRY = int(os.environ.get('ACCESS_TOKEN_EXPIRY'))
REGISTRATION_OTP_EXPIRY_TIME = int(
    os.environ.get('REGISTRATION_OTP_EXPIRY_TIME'))

DATA_UPLOAD_MAX_NUMBER_FIELDS = None

min_django_level = 'INFO'

min_level = 'DEBUG'
# error logging configs
# logging dictConfig configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # keep Django's default loggers
    'formatters': {
        'timestampthread': {
            'format': "%(asctime)s [%(pathname)s] [%(funcName)s][%(lineno)s][%(levelname)-5.5s] %(message)s",
        },
    },
    'handlers': {
        'logfile': {
            # optionally raise to INFO to not fill the log file too quickly
            'level': min_level,  # this level or higher goes to the log file
            'class': 'logging.handlers.RotatingFileHandler',
            # IMPORTANT: replace with your desired logfile name!
            # 'filename': os.path.join(BASE_DIR, '../logs/land_admin.log'),
            'filename':  os.path.join(BASE_DIR, "../logs/app.log"),
            'maxBytes': 50 * 10**6,  # will 50 MB do?
            'backupCount': 3,  # keep this many extra historical files
            'formatter': 'timestampthread'
        },
        'console': {
            'level': min_django_level,  # this level or higher goes to the console
            'class': 'logging.StreamHandler',
        },
        'mail_admins': {
            'level': min_django_level,
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': min_django_level,
            'propagate': True,
        },
    },
    'root': {
        'handlers': ['logfile', 'console'],
        'level': min_level,  # this level or higher goes to the console,
    },
}


django_heroku.settings(locals())
