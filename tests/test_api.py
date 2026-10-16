from collections.abc import Iterator
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_price_service
from app.db.models import Price
from app.main import create_app
from app.schemas.price import DateRange, Pagination
from app.services.exceptions import PriceNotFoundError
from app.services.price import PriceService

BTC_PRICE = Price(ticker="btc_usd", price=Decimal("81213.58"), timestamp=1792058071)


@pytest.fixture
def service() -> AsyncMock:
    return AsyncMock(spec=PriceService)


@pytest.fixture
def client(service: AsyncMock) -> Iterator[TestClient]:
    app = create_app()
    app.dependency_overrides[get_price_service] = lambda: service
    yield TestClient(app)


def test_ticker_is_required(client: TestClient) -> None:
    response = client.get("/prices/latest")

    assert response.status_code == 422


def test_unknown_ticker_rejected(client: TestClient, service: AsyncMock) -> None:
    response = client.get("/prices/latest", params={"ticker": "doge_usd"})

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["query", "ticker"]
    service.get_latest.assert_not_awaited()


def test_latest_price_returned(client: TestClient, service: AsyncMock) -> None:
    service.get_latest.return_value = BTC_PRICE

    response = client.get("/prices/latest", params={"ticker": "btc_usd"})

    assert response.status_code == 200
    assert response.json() == {"ticker": "btc_usd", "price": "81213.58", "timestamp": 1792058071}


def test_latest_price_not_found(client: TestClient, service: AsyncMock) -> None:
    service.get_latest.side_effect = PriceNotFoundError("btc_usd")

    response = client.get("/prices/latest", params={"ticker": "btc_usd"})

    assert response.status_code == 404


def test_prices_by_date_passes_filter(client: TestClient, service: AsyncMock) -> None:
    service.get_by_date.return_value = [BTC_PRICE]

    response = client.get(
        "/prices/by-date",
        params={"ticker": "BTC_USD", "date_from": 100, "date_to": 200, "limit": 10},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    service.get_by_date.assert_awaited_once_with(
        "btc_usd", DateRange(date_from=100, date_to=200), Pagination(limit=10, offset=0)
    )


def test_prices_by_date_rejects_inverted_range(client: TestClient, service: AsyncMock) -> None:
    response = client.get(
        "/prices/by-date", params={"ticker": "btc_usd", "date_from": 200, "date_to": 100}
    )

    assert response.status_code == 422
    service.get_by_date.assert_not_awaited()


def test_latest_prices_for_configured_tickers(client: TestClient, service: AsyncMock) -> None:
    service.get_latest_for_tickers.return_value = [BTC_PRICE]

    response = client.get("/prices")

    assert response.status_code == 200
    assert response.json() == [{"ticker": "btc_usd", "price": "81213.58", "timestamp": 1792058071}]
    service.get_latest_for_tickers.assert_awaited_once_with(("btc_usd", "eth_usd"))
