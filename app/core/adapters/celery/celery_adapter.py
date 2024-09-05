from celery import Celery
from celery.schedules import crontab

from app.dependencies import get_settings

settings = get_settings()

CELERY_BROCKER_URL = settings.REDIS_URL
CELERY_RESULT_BACKEND = settings.REDIS_URL

celery_app = Celery(
    broker=CELERY_BROCKER_URL,
    backend=CELERY_RESULT_BACKEND,
)


@celery_app.task
def my_task():
    print('Hello from my_task')
    return 1 + 2


celery_app.conf.broker_connection_retry_on_startup = True

# @celery_app.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
#     sender.add_periodic_task(10.0, my_task.s(), name='add every 10')

celery_app.conf.update(
    beat_schedule={
        'run-every-10-seconds': {
            'task': 'app.core.adapters.celery.celery_adapter.my_task',
            # 'schedule': 10.0,
            'schedule': crontab(minute="*/1", hour="*")
        }
    }
)

print('Celery app started')
