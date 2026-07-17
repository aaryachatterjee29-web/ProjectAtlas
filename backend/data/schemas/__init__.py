"""Provider-independent data schemas for the market data layer.

These Pydantic models are the canonical shapes that flow between
provider implementations and the rest of the application. They are
intentionally minimal and stable; provider-specific data (e.g. raw
Kite SDK objects) must be converted into these schemas before crossing
the provider boundary.

Why Pydantic
------------
Pydantic gives us:

* runtime validation at the boundary (provider -> service),
* immutability via ``frozen=True`` so downstream code cannot mutate
  a record it received,
* free JSON serialization for API responses,
* IDE / MyPy support for typed attributes.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class _StrictModel(BaseModel):
    """Base for all schemas: immutable, no extra fields, validate on assignment."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        validate_assignment=True,
    )


class Instrument(_StrictModel):
    """A tradable instrument as exposed by a market data provider.

    The (exchange, symbol) pair is the natural identifier; ``token`` is a
    provider-assigned integer ID used by some providers (e.g. Kite) to
    address instruments more efficiently than by string symbol.
    """

    exchange: str = Field(..., min_length=1, max_length=50)
    symbol: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    instrument_type: str = Field(..., min_length=1, max_length=20)
    currency: str = Field(default="INR", min_length=1, max_length=10)
    token: int | None = Field(default=None, ge=0)


class Quote(_StrictModel):
    """A real-time or near-real-time price quote for an instrument.

    ``timestamp`` reflects when the provider captured the quote, which
    may differ from when the application received it.
    """

    exchange: str = Field(..., min_length=1, max_length=50)
    symbol: str = Field(..., min_length=1, max_length=50)
    last_price: Decimal
    bid: Decimal | None = None
    ask: Decimal | None = None
    bid_qty: int | None = Field(default=None, ge=0)
    ask_qty: int | None = Field(default=None, ge=0)
    volume: int | None = Field(default=None, ge=0)
    timestamp: datetime


class HistoricalPrice(_StrictModel):
    """One OHLCV bar of historical price data for an instrument.

    Adjusted prices reflect corporate actions (splits, dividends); the
    raw ``close`` reflects the unadjusted close. ``volume`` is in
    provider-native units (typically shares / contracts).
    """

    exchange: str = Field(..., min_length=1, max_length=50)
    symbol: str = Field(..., min_length=1, max_length=50)
    date: date
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    adjusted_close: Decimal
    volume: int = Field(..., ge=0)
    interval: str = Field(default="day", min_length=1, max_length=20)
