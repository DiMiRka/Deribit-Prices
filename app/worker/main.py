from app.core.config import get_settings
from app.worker.celery_app import create_celery_app

celery_app = create_celery_app(get_settings())
