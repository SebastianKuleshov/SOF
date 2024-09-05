from app.core.adapters.celery.celery_adapter import celery_app


@celery_app.task()
async def generate_and_send_report_task() -> None:
    print('Generating and sending report...')