import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BulletinBoard.settings')

app = Celery('BulletinBoard')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'newsletters_by_week': {
        'task': 'advert.tasks.newsletters',
        'schedule': crontab(day_of_week='2', hour="5", minute="50"),
        'args': (),
    },
}
