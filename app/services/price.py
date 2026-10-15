from collections.abc import Sequence

from app.db.models import Price
from app.repositories.price import PriceRepository
from app.schemas.price import DateRange, Pagination
from app.services.exceptions import PriceNotFoundError


class PriceService:
    def __init__(self, repository: PriceRepository) -> None:
        self._repository = repository

    async def get_all(self, ticker: str, pagination: Pagination) -> Sequence[Price]:
        return await self._repository.list_by_ticker(
            ticker, limit=pagination.limit, offset=pagination.offset
        )

    async def get_latest(self, ticker: str) -> Price:
        price = await self._repository.get_latest(ticker)
        if price is None:
            raise PriceNotFoundError(ticker)
        return price

    async def get_by_date(
        self, ticker: str, date_range: DateRange, pagination: Pagination
    ) -> Sequence[Price]:
        return await self._repository.list_by_ticker(
            ticker,
            limit=pagination.limit,
            offset=pagination.offset,
            date_from=date_range.date_from,
            date_to=date_range.date_to,
        )
