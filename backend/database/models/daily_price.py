"""DailyPrice model.

One row per stock per trading day. Stores raw OHLC, adjusted close, volume,
and corporate-action fields (dividends, splits).

Relationships
-------------
* :class:`~backend.database.models.stock.Stock` — each price row belongs to
  exactly one stock via ``stock_id`` foreign key.

Design decisions
----------------
* ``Numeric(20, 8)`` is used for prices. This is deliberately wider than
  is typically needed (8 decimal places) to handle fractional-share and
  crypto-adjacent contexts. ``Numeric`` avoids the floating-point drift
  that is unacceptable for monetary values.
* ``volume`` is ``BigInteger`` — historical equity volume can exceed 2^31.
* ``(stock_id, date)`` is unique so re-ingesting the same day is a no-op
  or upsert rather than a duplicate.
* An index on ``date`` supports range scans ("all prices between
  ``2020-01-01`` and ``2020-12-31``") that drive most backtest queries.
* ``dividend`` and ``stock_split`` default to 0 to keep the schema simple
  for ingesting data sources that omit them on non-event days.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Date, ForeignKey, Index, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from backend.database.models.stock import Stock


class DailyPrice(Base, TimestampMixin):
    """OHLCV + corporate actions for a single stock on a single trading day."""

    __tablename__ = "daily_prices"
    __table_args__ = (
        UniqueConstraint("stock_id", "date", name="uq_daily_prices_stock_date"),
        Index("ix_daily_prices_date", "date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    stock_id: Mapped[int] = mapped_column(
        ForeignKey("stocks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)

    open: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    high: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    low: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    close: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)

    adjusted_close: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    volume: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)

    dividend: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False, default=Decimal("0"))
    stock_split: Mapped[Decimal] = mapped_column(
        Numeric(20, 8), nullable=False, default=Decimal("0")
    )

    stock: Mapped[Stock] = relationship(back_populates="daily_prices")

    def __repr__(self) -> str:
        return f"<DailyPrice stock_id={self.stock_id} date={self.date.isoformat()}>"
