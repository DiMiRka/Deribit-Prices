"""create prices table

Revision ID: 0fd4a0f9d256
Revises:
Create Date: 2026-10-14 19:05:23.590771

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0fd4a0f9d256"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "prices",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("ticker", sa.String(length=32), nullable=False),
        sa.Column("price", sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column("timestamp", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_prices")),
    )
    op.create_index("ix_prices_ticker_timestamp", "prices", ["ticker", "timestamp"])


def downgrade() -> None:
    op.drop_index("ix_prices_ticker_timestamp", table_name="prices")
    op.drop_table("prices")
