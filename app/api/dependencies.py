from collections.abc import AsyncIterator
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


def get_pagination(
    limit: Annotated[int, Query(ge=1, le=MAX_LIMIT)] = DEFAULT_LIMIT,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> Pagination:
    return Pagination(limit=limit, offset=offset)


def get_date_range(
    date_from: Annotated[int | None, Query(ge=0, description="UNIX timestamp, inclusive")] = None,
    date_to: Annotated[int | None, Query(ge=0, description="UNIX timestamp, inclusive")] = None,
) -> DateRange:
    if date_from is not None and date_to is not None and date_from > date_to:
        raise RequestValidationError(
            [
                {
                    "type": "value_error",
                    "loc": ("query", "date_from"),
                    "msg": "date_from must be less than or equal to date_to",
                    "input": date_from,
                }
            ]
        )
    return DateRange(date_from=date_from, date_to=date_to)


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
