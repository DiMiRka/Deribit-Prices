from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Price


class PriceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add_many(self, prices: Sequence[Price]) -> None:
        self._session.add_all(prices)
        await self._session.commit()

    async def list_by_ticker(
        self,
        ticker: str,
        *,
        limit: int,
        offset: int,
        date_from: int | None = None,
        date_to: int | None = None,
    ) -> Sequence[Price]:
        query = select(Price).where(Price.ticker == ticker)
        if date_from is not None:
            query = query.where(Price.timestamp >= date_from)
        if date_to is not None:
            query = query.where(Price.timestamp <= date_to)
        query = query.order_by(Price.timestamp).limit(limit).offset(offset)
        return (await self._session.scalars(query)).all()

    async def get_latest(self, ticker: str) -> Price | None:
        query = (
            select(Price).where(Price.ticker == ticker).order_by(Price.timestamp.desc()).limit(1)
        )
        return await self._session.scalar(query)
