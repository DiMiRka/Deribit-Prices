import aiohttp
from pydantic import ValidationError

from app.clients.deribit.exceptions import (
    DeribitAPIError,
    DeribitNetworkError,
    DeribitResponseError,
)
from app.clients.deribit.schemas import IndexPrice, IndexPriceResponse

MICROSECONDS_IN_SECOND = 1_000_000


class DeribitClient:
    def __init__(self, session: aiohttp.ClientSession, base_url: str, timeout: float) -> None:
        self._session = session
        self._base_url = base_url.rstrip("/")
        self._timeout = aiohttp.ClientTimeout(total=timeout)

    async def get_index_price(self, ticker: str) -> IndexPrice:
        url = f"{self._base_url}/public/get_index_price"
        try:
            async with self._session.get(
                url, params={"index_name": ticker}, timeout=self._timeout
            ) as response:
                status = response.status
                body = await response.read()
        except (aiohttp.ClientError, TimeoutError) as exc:
            raise DeribitNetworkError(f"Request to Deribit failed: {exc!r}") from exc

        try:
            payload = IndexPriceResponse.model_validate_json(body)
        except ValidationError as exc:
            raise DeribitResponseError(f"Unexpected Deribit response, HTTP {status}") from exc

        if payload.error is not None:
            raise DeribitAPIError(payload.error.code, payload.error.message)
        if payload.result is None:
            raise DeribitResponseError(f"Deribit response without result, HTTP {status}")

        return IndexPrice(
            ticker=ticker,
            price=payload.result.index_price,
            timestamp=payload.us_out // MICROSECONDS_IN_SECOND,
        )
