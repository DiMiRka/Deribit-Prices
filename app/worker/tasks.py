import asyncio

import aiohttp
from celery import shared_task

from app.clients.deribit import DeribitClient
from app.core.config import Settings, get_settings
from app.db.session import Database
from app.repositories.price import PriceRepository
from app.schemas.price import Ticker
from app.services.collector import PriceCollector


async def run_collection(settings: Settings) -> int:
    database = Database(settings.database_url)
    try:
        async with aiohttp.ClientSession() as http_session, database.session() as db_session:
            client = DeribitClient(
                http_session, settings.deribit_base_url, settings.deribit_timeout_seconds
            )
            collector = PriceCollector(client, PriceRepository(db_session), tuple(Ticker))
            collected = await collector.collect()
    finally:
        await database.dispose()
    return len(collected)


@shared_task(name="collect_prices")
def collect_prices() -> int:
    return asyncio.run(run_collection(get_settings()))
