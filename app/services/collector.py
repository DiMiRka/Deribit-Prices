import asyncio
from collections.abc import Sequence

from loguru import logger

from app.clients.deribit import DeribitClient, DeribitError, IndexPrice
from app.db.models import Price
from app.repositories.price import PriceRepository


class PriceCollector:
    def __init__(
        self, client: DeribitClient, repository: PriceRepository, tickers: Sequence[str]
    ) -> None:
        self._client = client
        self._repository = repository
        self._tickers = tickers

    async def collect(self) -> list[IndexPrice]:
        results = await asyncio.gather(
            *(self._client.get_index_price(ticker) for ticker in self._tickers),
            return_exceptions=True,
        )

        collected: list[IndexPrice] = []
        for ticker, result in zip(self._tickers, results, strict=True):
            if isinstance(result, DeribitError):
                logger.warning(f"Failed to fetch {ticker} index price: {result}")
            elif isinstance(result, BaseException):
                raise result
            else:
                collected.append(result)

        if collected:
            await self._repository.add_many(
                [
                    Price(ticker=item.ticker, price=item.price, timestamp=item.timestamp)
                    for item in collected
                ]
            )
        logger.info("Saved {} of {} index prices", len(collected), len(self._tickers))
        return collected
