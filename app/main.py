from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.prices import router as prices_router
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.db.session import Database


def create_app() -> FastAPI:
    settings = get_settings()
    setup_logging(settings.log_level)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        database = Database(settings.database_url)
        app.state.database = database
        try:
            yield
        finally:
            await database.dispose()

    app = FastAPI(title="Deribit Prices API", version="0.1.0", lifespan=lifespan)
    app.include_router(prices_router)
    return app
