from collections.abc import Sequence

from fastapi import APIRouter, HTTPException, status

from app.api.dependencies import (
    DateRangeDep,
    PaginationDep,
    PriceServiceDep,
    TickerDep,
)
from app.db.models import Price
from app.schemas.price import PriceRead, Ticker
from app.services.exceptions import PriceNotFoundError

router = APIRouter(prefix="/prices", tags=["prices"])


@router.get("", response_model=list[PriceRead], summary="Актуальная цена для каждого тикера")
async def get_latest_prices(service: PriceServiceDep) -> Sequence[Price]:
    return await service.get_latest_for_tickers(tuple(Ticker))


@router.get("/history", response_model=list[PriceRead], summary="Все сохранённые цены для тикера")
async def get_price_history(
    ticker: TickerDep, pagination: PaginationDep, service: PriceServiceDep
) -> Sequence[Price]:
    return await service.get_all(ticker, pagination)


@router.get("/latest", response_model=PriceRead, summary="Последняя цена по тикеру")
async def get_latest_price(ticker: TickerDep, service: PriceServiceDep) -> Price:
    try:
        return await service.get_latest(ticker)
    except PriceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/by-date", response_model=list[PriceRead], summary="Цены для тикера по датам")
async def get_prices_by_date(
    ticker: TickerDep,
    date_range: DateRangeDep,
    pagination: PaginationDep,
    service: PriceServiceDep,
) -> Sequence[Price]:
    return await service.get_by_date(ticker, date_range, pagination)
