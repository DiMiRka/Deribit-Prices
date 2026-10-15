from collections.abc import Sequence

from fastapi import APIRouter, HTTPException, status

from app.api.dependencies import DateRangeDep, PaginationDep, PriceServiceDep, TickerDep
from app.db.models import Price
from app.schemas.price import PriceRead
from app.services.exceptions import PriceNotFoundError

router = APIRouter(prefix="/prices", tags=["prices"])


@router.get("", response_model=list[PriceRead], summary="All stored prices for a ticker")
async def get_all_prices(
    ticker: TickerDep, pagination: PaginationDep, service: PriceServiceDep
) -> Sequence[Price]:
    return await service.get_all(ticker, pagination)


@router.get("/latest", response_model=PriceRead, summary="Latest price for a ticker")
async def get_latest_price(ticker: TickerDep, service: PriceServiceDep) -> Price:
    try:
        return await service.get_latest(ticker)
    except PriceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/by-date", response_model=list[PriceRead], summary="Prices for a ticker by date")
async def get_prices_by_date(
    ticker: TickerDep,
    date_range: DateRangeDep,
    pagination: PaginationDep,
    service: PriceServiceDep,
) -> Sequence[Price]:
    return await service.get_by_date(ticker, date_range, pagination)
