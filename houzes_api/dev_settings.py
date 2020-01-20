
CORS_ORIGIN_ALLOW_ALL = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'houzes_local',
        'USER': 'postgres',
        'PASSWORD': 'wsit9748',
        'HOST': 'localhost',
        'PORT': '5432',
    },
}

CLIENT_ID = "enKpO5OOK8AFVY2U5fuR5l3uD9UH4mGKrJXpTbGJ"
CLIENT_SECRET = "vQgrl1HEfiUktjgXFmC3wK5t7JkU6L6mDwDKkBfb4h4F5yAslvaKXs9kKcH5g0Gcmwi67CC8Lhi1p9Bd0Roo9kexnC9VRanLp1SMmzrskfjLTJwyUALFbckI0j58QL1Q"

BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
