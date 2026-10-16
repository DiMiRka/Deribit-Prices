import datetime as dt
from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, computed_field


class Ticker(StrEnum):
    BTC_USD = "btc_usd"
    ETH_USD = "eth_usd"

    @classmethod
    def _missing_(cls, value: object) -> Self | None:
        if isinstance(value, str):
            normalized = value.strip().lower()
            return next((member for member in cls if member.value == normalized), None)
        return None


class PriceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ticker: str
    price: Decimal
    timestamp: int

    @computed_field  # type: ignore[prop-decorator]
    @property
    def datetime(self) -> dt.datetime:
        return dt.datetime.fromtimestamp(self.timestamp, tz=dt.UTC)


@dataclass(frozen=True, slots=True)
class Pagination:
    limit: int
    offset: int


@dataclass(frozen=True, slots=True)
class DateRange:
    date_from: int | None
    date_to: int | None
