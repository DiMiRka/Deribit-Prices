import asyncio

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import get_settings
from app.core.logging import setup_logging
from app.db import models  # noqa: F401  registers models in Base.metadata
from app.db.base import Base

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = get_settings().database_url.render_as_string(hide_password=False)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    engine = create_async_engine(get_settings().database_url, poolclass=pool.NullPool)

    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await engine.dispose()


setup_logging(get_settings().log_level)

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_async_migrations())
