from celery import shared_task
from celery.task import periodic_task, task
import datetime
from houzes_api.celery import app


@app.task()
def test_celery():
    print("Celery works!")


@task()
@periodic_task(run_every=datetime.timedelta(seconds=10))
def periodic_task():
    print("periodic_task is running...")
