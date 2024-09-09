from celery import Celery
from celery.schedules import crontab

from app.dependencies import get_settings

settings = get_settings()

CELERY_BROCKER_URL = settings.REDIS_URL
CELERY_RESULT_BACKEND = settings.REDIS_URL

celery_app = Celery(
    broker=CELERY_BROCKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=['app.common.tasks']
)

celery_app.conf.broker_connection_retry_on_startup = True

celery_app.conf.timezone = settings.TIMEZONE


# The schedule is based on Europe/Kiev timezone
celery_app.conf.beat_schedule = {
    'test': {
        'task': 'app.common.tasks.generate_and_send_report_task',
        'schedule': crontab(minute='*/1')
    },
    'run-every-hour': {
        'task': 'app.common.tasks.generate_and_send_report_task',
        'schedule': crontab(
            minute='0',
            hour='9,12,15',
            day_of_week='1-5',
            day_of_month='*',
            month_of_year='*'
        )
    },
    'run-every-mid-hour': {
        'task': 'app.common.tasks.generate_and_send_report_task',
        'schedule': crontab(
            minute='30',
            hour='10,13,16',
            day_of_week='1-5',
            day_of_month='*',
            month_of_year='*'
        )
    }
}
