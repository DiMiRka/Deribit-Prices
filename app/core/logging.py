import inspect
import logging
import sys

from loguru import logger

LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)
THIRD_PARTY_LOGGERS = ("uvicorn", "uvicorn.error", "uvicorn.access", "celery")


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = inspect.currentframe(), 0
        while frame is not None and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging(level: str) -> None:
    logger.remove()
    logger.add(sys.stderr, level=level, format=LOG_FORMAT)

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    for name in THIRD_PARTY_LOGGERS:
        third_party_logger = logging.getLogger(name)
        third_party_logger.handlers.clear()
        third_party_logger.propagate = True
