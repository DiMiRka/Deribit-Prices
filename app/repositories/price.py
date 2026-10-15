from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Price


class PriceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add_many(self, prices: Sequence[Price]) -> None:
        self._session.add_all(prices)
        await self._session.commit()
