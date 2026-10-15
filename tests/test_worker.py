from unittest.mock import AsyncMock

import pytest

from app.core.config import Settings
from app.worker import tasks
from app.worker.celery_app import create_celery_app


def test_beat_runs_registered_collect_task(monkeypatch: pytest.MonkeyPatch) -> None:
    run_collection = AsyncMock(return_value=2)
    monkeypatch.setattr(tasks, "run_collection", run_collection)
    celery_app = create_celery_app(Settings(_env_file=None, collect_interval_seconds=60))

    schedule = celery_app.conf.beat_schedule["collect-index-prices"]
    task = celery_app.tasks[schedule["task"]]

    assert schedule["schedule"] == 60
    assert task.apply().get() == 2
    run_collection.assert_awaited_once()
