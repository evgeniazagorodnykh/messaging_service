from tasks.tasks import celery
from celery.schedules import crontab

celery.conf.broker_connection_retry_on_startup = True
celery.conf.beat_schedule = {
    'notify-unread-messages-every-5-minutes': {
        'task': 'tasks.tasks.notify_unread_messages',
        'schedule': crontab(minute='*/5'),  # каждые 5 минут
    },
}
