from typing import Any

from celery import Celery
from celery.schedules import crontab
from celery.signals import setup_logging as celery_setup_logging

from app.core.config import Settings
from app.core.logging import setup_logging

TASK_EXPIRES_SECONDS = 60


def create_celery_app(settings: Settings) -> Celery:
    def configure_logging(**kwargs: Any) -> None:
        setup_logging(settings.log_level)

    celery_setup_logging.connect(configure_logging, weak=False, dispatch_uid="app_logging")

    celery_app = Celery("deribit_prices", broker=settings.redis_url, include=["app.worker.tasks"])
    celery_app.conf.update(
        timezone="UTC",
        task_ignore_result=True,
        broker_connection_retry_on_startup=True,
        beat_schedule={
            "collect-index-prices": {
                "task": "collect_prices",
                "schedule": crontab.from_string(settings.collect_schedule),
                "options": {"expires": TASK_EXPIRES_SECONDS},
            },
        },
    )
    return celery_app
