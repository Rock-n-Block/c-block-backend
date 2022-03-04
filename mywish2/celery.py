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
        'schedule': crontab(minute='*/60'),
        'args': (config.network.rpc_endpoint, False),
    },
    'check_dead_wallets_test': {
        'task': 'scanner.tasks.check_dead_wallets',
        'schedule': crontab(minute='*/1'),
        'args': (config.test_network.rpc_endpoint, True),
    },
    'check_and_send_notifications': {
        'task': 'scanner.tasks.check_and_send_notifications',
        'schedule': crontab(minute=f'*/{int(config.network.day_seconds / 60)}'),
        'args': (
            config.network.rpc_endpoint,
            False,
            config.network.day_seconds,
            config.network.confirmation_checkpoints
        ),
    },
    'check_and_send_notifications_test': {
        'task': 'scanner.tasks.check_and_send_notifications',
        'schedule': crontab(minute=f'*/{int(config.test_network.day_seconds / 60)}'),
        'args': (
            config.test_network.rpc_endpoint,
            True,
            config.test_network.day_seconds,
            config.test_network.confirmation_checkpoints
        ),
    },
}

app.autodiscover_tasks()
