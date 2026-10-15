from dataclasses import dataclass
from decimal import Decimal

from pydantic import BaseModel, Field


@dataclass(frozen=True, slots=True)
class IndexPrice:
    ticker: str
    price: Decimal
    timestamp: int


class RPCError(BaseModel):
    code: int
    message: str


class IndexPriceResult(BaseModel):
    index_price: Decimal


class IndexPriceResponse(BaseModel):
    result: IndexPriceResult | None = None
    error: RPCError | None = None
    us_out: int = Field(alias="usOut")
