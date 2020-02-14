from __future__ import absolute_import
import os
from celery import Celery
import datetime
from django.conf import settings

# load_env()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'houzes_api.settings')

app = Celery('houzes_api')

app.config_from_object('django.conf:settings', namespace="CELERY")

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


