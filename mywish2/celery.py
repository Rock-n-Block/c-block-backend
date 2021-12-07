import os

from celery import Celery
from celery.schedules import crontab

from mywish2.settings import config

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mywish2.settings')

app = Celery('mywish2')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule = {
    'check_dead_wallets': {
        'task': 'scanner.tasks.check_dead_wallets',
        'schedule': crontab(hour='*/1'),
        'args': (config.TEST_ENDPOINT, True),
    },
    'check_dead_wallets_test': {
        'task': 'scanner.tasks.check_dead_wallets',
        'schedule': crontab(hour='*/1'),
        'args': (config.ENDPOINT, False),
    },
}

app.autodiscover_tasks()
