from decimal import Decimal
from unittest.mock import AsyncMock

from app.clients.deribit import DeribitClient, DeribitNetworkError, IndexPrice
from app.repositories.price import PriceRepository
from app.services.collector import PriceCollector

BTC = IndexPrice(ticker="btc_usd", price=Decimal("80903.36"), timestamp=1792048859)
ETH = IndexPrice(ticker="eth_usd", price=Decimal("2360.2"), timestamp=1792048859)


def make_client(responses: dict[str, IndexPrice | Exception]) -> AsyncMock:
    client = AsyncMock(spec=DeribitClient)

    async def get_index_price(ticker: str) -> IndexPrice:
        response = responses[ticker]
        if isinstance(response, Exception):
            raise response
        return response

    client.get_index_price.side_effect = get_index_price
    return client


def saved_rows(repository: AsyncMock) -> list[tuple[str, Decimal, int]]:
    (prices,) = repository.add_many.await_args.args
    return [(price.ticker, price.price, price.timestamp) for price in prices]


async def test_saves_prices_for_all_tickers() -> None:
    repository = AsyncMock(spec=PriceRepository)
    collector = PriceCollector(
        make_client({"btc_usd": BTC, "eth_usd": ETH}), repository, ("btc_usd", "eth_usd")
    )

    collected = await collector.collect()

    assert collected == [BTC, ETH]
    assert saved_rows(repository) == [
        ("btc_usd", Decimal("80903.36"), 1792048859),
        ("eth_usd", Decimal("2360.2"), 1792048859),
    ]


async def test_failed_ticker_does_not_block_others() -> None:
    repository = AsyncMock(spec=PriceRepository)
    client = make_client({"btc_usd": DeribitNetworkError("timeout"), "eth_usd": ETH})
    collector = PriceCollector(client, repository, ("btc_usd", "eth_usd"))

    collected = await collector.collect()

    assert collected == [ETH]
    assert saved_rows(repository) == [("eth_usd", Decimal("2360.2"), 1792048859)]
