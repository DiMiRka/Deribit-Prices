import math
from collections.abc import AsyncIterator, Callable
from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends, Query, Request
from fastapi.exceptions import RequestValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import Database
from app.repositories.price import PriceRepository
from app.schemas.price import DateRange, Pagination, Ticker
from app.services.price import PriceService

DEFAULT_LIMIT = 100
MAX_LIMIT = 1000
DATE_DESCRIPTION = (
    "Дата 2026-10-16 (с 00:00) или дата и время 2026-10-16 12:30, время в UTC, граница включительно"
)


def get_pagination(
    limit: Annotated[int, Query(ge=1, le=MAX_LIMIT)] = DEFAULT_LIMIT,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> Pagination:
    return Pagination(limit=limit, offset=offset)


def _validation_error(field: str, message: str, value: object) -> RequestValidationError:
    return RequestValidationError(
        [{"type": "value_error", "loc": ("query", field), "msg": message, "input": value}]
    )


def _to_unix(field: str, value: datetime | None, rounding: Callable[[float], int]) -> int | None:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    timestamp = rounding(value.timestamp())
    if timestamp < 0:
        raise _validation_error(field, "Date must not be earlier than 1970-01-01T00:00:00Z", value)
    return timestamp


def get_date_range(
    date_from: Annotated[datetime | None, Query(description=DATE_DESCRIPTION)] = None,
    date_to: Annotated[datetime | None, Query(description=DATE_DESCRIPTION)] = None,
) -> DateRange:
    from_timestamp = _to_unix("date_from", date_from, math.ceil)
    to_timestamp = _to_unix("date_to", date_to, math.floor)
    if from_timestamp is not None and to_timestamp is not None and from_timestamp > to_timestamp:
        raise _validation_error(
            "date_from", "date_from must be less than or equal to date_to", date_from
        )
    return DateRange(date_from=from_timestamp, date_to=to_timestamp)


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    database: Database = request.app.state.database
    async with database.session() as session:
        yield session


def get_price_service(session: Annotated[AsyncSession, Depends(get_session)]) -> PriceService:
    return PriceService(PriceRepository(session))


TickerDep = Annotated[Ticker, Query(description="Deribit index name")]
PaginationDep = Annotated[Pagination, Depends(get_pagination)]
DateRangeDep = Annotated[DateRange, Depends(get_date_range)]
PriceServiceDep = Annotated[PriceService, Depends(get_price_service)]
