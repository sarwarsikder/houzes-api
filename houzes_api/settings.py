"""
Django settings for houzes_api project.

Generated by 'django-admin startproject' using Django 2.2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

default_headers = (
    'x-requested-with',
    'content-type',
    'accept',
    'origin',
    'authorization',
    'x-csrftoken',
    'user-agent',
    'accept-encoding',
)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = '3i*wqdxveir3$u%ijfo7m@fb(9l@s)bq0&q4mt*n5@h3990^j3'
SECRET_KEY = '6T9TUuaaxBOlrcQz0JN5bdZREly05MABvpuGBSNbZO8JOJ0f3MK7SwmyO0vpWumIlcRkSnXe9mfDqLl6tmjYP1xkvM7vIuy4GPSSGHoV6DU9xicEkuscFriS6SZGuXaB'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'api',
    'rest_framework',
    'storages',
    'oauth2_provider',
    'social_django',
    'rest_framework_social_oauth2',
    'corsheaders',
    'admin_panel',
    'whitenoise',
    'notifications',
    'celery_task',
    'django_celery_beat',
]
APP_ENV = 'PROD'  # PROD, DEV

# Application definition


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'oauth2_provider.middleware.OAuth2TokenMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'houzes_api.urls'
CORS_ORIGIN_ALLOW_ALL = True
# CORS_ORIGIN_WHITELIST = ('localhost:4200')
CORS_ORIGIN_REGEX_WHITELIST = (
    'localhost:4200',
    'https://www.google.com',
    'http://houzes.com.s3-website-us-east-1.amazonaws.com',
)
CORS_ALLOW_HEADERS = default_headers + (
    'cache-control',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

REST_FRAMEWORK = {
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser'
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
        'rest_framework_social_oauth2.authentication.SocialAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
}

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'oauth2_provider.backends.OAuth2Backend',
    # Facebook OAuth2
    'social_core.backends.facebook.FacebookAppOAuth2',
    'social_core.backends.facebook.FacebookOAuth2',
    # Google OAuth2
    'social_core.backends.google.GoogleOAuth2',

    # django-rest-framework-social-oauth2
    'rest_framework_social_oauth2.backends.DjangoOAuth2',
)

OAUTH2_PROVIDER = {
    'SCOPES': {
        # 'users': 'user details',
        'read': 'Read scope',
        'write': 'Write scope',
        'groups': 'Access to your groups',
        'introspection': 'introspection'
    },
    'ACCESS_TOKEN_EXPIRE_SECONDS': 864000,  # 10 Day.
}

WSGI_APPLICATION = 'houzes_api.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'houzes_staging',
        'USER': 'postgres',
        'PASSWORD': 'wsit97480',
        'HOST': 'houzes-db.cacdyf2lutyz.us-east-1.rds.amazonaws.com',
        'PORT': '5432',
    },
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

AUTH_USER_MODEL = "api.User"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/
STATIC_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static')
# STATIC_URL = '/static/'

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "admin_panel/static"),
]

# Facebook configuration
# SOCIAL_AUTH_FACEBOOK_KEY = '931483470524585'
# SOCIAL_AUTH_FACEBOOK_SECRET = '4c86f1286740afc5917189caed4a221f'
SOCIAL_AUTH_FACEBOOK_KEY = '781060575665251'
SOCIAL_AUTH_FACEBOOK_SECRET = 'ad35c15941004eeb8c34d5d26f36bc07'

# Define SOCIAL_AUTH_FACEBOOK_SCOPE to get extra permissions from facebook. Email is not sent by default, to get it, you must request the email permission:
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
    'fields': 'id, name, email'
}

# Google configuration
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '1SHT_DbIoJODMssT1rnbIBGn'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = '468965753089-g34blpbr5huekl0r0sohp9ocj2pa9dsk.apps.googleusercontent.com'

# Define SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE to get extra permissions from Google.
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
]


# nadim's key
AWS_ACCESS_KEY = "AKIAIHTBVHHY6BGFFMIQ"
AWS_SECRET_KEY = "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"
AWS_REGION = "us-east-2"

S3_BUCKET_NAME = "houzes"
# S3 Settings
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_S3_SECURE_URLS = True  # use http instead of https
AWS_QUERYSTRING_AUTH = False  # don't add complex authentication-related query parameters for requests
AWS_S3_REGION_NAME = "us-east-2"

# nadim's key
AWS_S3_ACCESS_KEY_ID = "AKIAIHTBVHHY6BGFFMIQ"
AWS_S3_SECRET_ACCESS_KEY = "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"

AWS_STORAGE_BUCKET_NAME = 'houzes'

AWS_DEFAULT_ACL = None

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'support@houzes.com'
EMAIL_HOST_PASSWORD = 'Success6'
# EMAIL_HOST_USER = 'support@realacquisitions.com'
# EMAIL_HOST_PASSWORD = 'Reboot2@18'
EMAIL_USE_TLS = True
# EMAIL_USE_SSL = True


CLIENT_ID = "b4eGPYQSTehw9G6sv36G8mXWXuW3qWd5z3EL4qpq"
CLIENT_SECRET = "NzrpAlEBLOE8RN7bbbFSVAF8Q8lm3DqFgUlwLZ5gS7ribxsiLfBO5F659KjDkfgjHNAvvplv8hSsTpjQP5YJTFeMHsTubkGq0Eero6jqWIJgVu8tx29pfvTczKatDKny"

# POWER_TRACE_CREDENTIALS
POWER_TRACE_HOST = "http://powertrace-service.ratoolkit.com:8080/ra-powertrace/"
# POWER_TRACE_HOST = "http://18.188.43.8:8080/ra-powertrace/"
POWER_TRACE_CLIENT_ID = "HQARK3QZDPLLBWSMVY0X2C5UJ2B15YQJSIY"
POWER_TRACE_CLIENT_SECRET = "URBVBVBDDJ2E2JEBJEO84594T546VJVBKJGB"

FETCH_OWNER_INFO_HOST = 'http://owner-search.houzes.com:8080/'
FETCH_OWNER_INFO_CLIENT_ID = 'ZDPLLBHQARK3QWSMVY0X2B15YQJSIYC5UJ2'
FETCH_OWNER_INFO_CLIENT_SECRET = 'RBVUBV6VJVBKJBDDJ2E2JEBJEO84594T54GB'

##SANDBOX
# AUTHORIZE_DOT_NET_MERCHANT_AUTH_NAME = '5K7ntL4d'
# AUTHORIZE_DOT_NET_MERCHANT_AUTH_TRANSACTION_KEY = '57m6DyFB5s3Lsx8s'

# MERCHANT
AUTHORIZE_DOT_NET_MERCHANT_AUTH_NAME = '8EdnVqPD5j98'
AUTHORIZE_DOT_NET_MERCHANT_AUTH_TRANSACTION_KEY = '86c895L2TgL3wB83'

# ## PROD
CELERY_BROKER_URL = 'redis://houzes-redis.pafft5.ng.0001.use1.cache.amazonaws.com:6379'
CELERY_RESULT_BACKEND = 'redis://houzes-redis.pafft5.ng.0001.use1.cache.amazonaws.com:6379'

# ## LOCAL
# CELERY_BROKER_URL = 'redis://localhost:6379'
# CELERY_RESULT_BACKEND = 'redis://localhost:6379'

CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'


WEB_APP_URL='houzes.com'

# MAILER_WIZARD_MICRO_SERVICE_URL = 'http://18.188.43.8:8111/mailer-service/send-mailer-data/'
# MAILER_WIZARD_MICRO_SERVICE_DOMAIN = 'http://18.188.43.8:8111/'
MAILER_WIZARD_MICRO_SERVICE_DOMAIN = 'http://powertrace-service.ratoolkit.com:8111/'
try:
    if APP_ENV is 'DEV':
        from .dev_settings import *
except ImportError:
    pass
