from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


class Database:
    def __init__(self, url: URL) -> None:
        self.engine = create_async_engine(url, pool_pre_ping=True)
        self.session_factory = async_sessionmaker(self.engine, expire_on_commit=False)

    def session(self) -> AsyncSession:
        return self.session_factory()

    async def dispose(self) -> None:
        await self.engine.dispose()
