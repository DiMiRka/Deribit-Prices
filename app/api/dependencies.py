from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Query, Request
from fastapi.exceptions import RequestValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.session import Database
from app.repositories.price import PriceRepository
from app.schemas.price import DateRange, Pagination
from app.services.price import PriceService

DEFAULT_LIMIT = 100
MAX_LIMIT = 1000


def get_ticker(
    ticker: Annotated[str, Query(description="Index name")],
    settings: Annotated[Settings, Depends(get_settings)],
) -> str:
    normalized = ticker.strip().lower()
    if normalized not in settings.tickers:
        raise RequestValidationError(
            [
                {
                    "type": "value_error",
                    "loc": ("query", "ticker"),
                    "msg": f"Unknown ticker, expected one of: {', '.join(settings.tickers)}",
                    "input": ticker,
                }
            ]
        )
    return normalized


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


SettingsDep = Annotated[Settings, Depends(get_settings)]
TickerDep = Annotated[str, Depends(get_ticker)]
PaginationDep = Annotated[Pagination, Depends(get_pagination)]
DateRangeDep = Annotated[DateRange, Depends(get_date_range)]
PriceServiceDep = Annotated[PriceService, Depends(get_price_service)]
