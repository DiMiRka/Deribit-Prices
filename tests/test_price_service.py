from unittest.mock import AsyncMock

import pytest

from app.repositories.price import PriceRepository
from app.services.exceptions import PriceNotFoundError
from app.services.price import PriceService


async def test_latest_raises_when_no_prices() -> None:
    repository = AsyncMock(spec=PriceRepository)
    repository.get_latest.return_value = None

    with pytest.raises(PriceNotFoundError):
        await PriceService(repository).get_latest("btc_usd")
