import logging
from collections.abc import Iterator

import pytest
from loguru import logger

from app.core.logging import setup_logging


@pytest.fixture
def captured_messages() -> Iterator[list[str]]:
    root_handlers = logging.root.handlers[:]
    root_level = logging.root.level
    messages: list[str] = []

    setup_logging("DEBUG")
    logger.add(messages.append, format="{level}|{message}", level="DEBUG")
    yield messages

    logger.remove()
    logging.root.handlers[:] = root_handlers
    logging.root.setLevel(root_level)


def test_stdlib_logging_routed_to_loguru(captured_messages: list[str]) -> None:
    logging.getLogger("some.library").warning("disk %s", "full")

    assert any(message.startswith("WARNING|disk full") for message in captured_messages)
