"""Stock model.

Represents a tradable instrument (e.g. an equity) tracked by the platform.
The ``ticker`` + ``exchange`` pair is unique because the same ticker symbol
can list on multiple exchanges (e.g. "AAPL" on NASDAQ vs "AAPL" on a
foreign venue). For most US-only workflows ``exchange`` is constant, but
the composite constraint future-proofs the schema for global data.

Relationships
-------------
* :class:`~backend.database.models.daily_price.DailyPrice` — one stock has
  many daily price rows (cascade delete).
* :class:`~backend.database.models.update_log.UpdateLog` — one stock has
  many update log entries (cascade delete).

Design decisions
----------------
* ``is_active`` is a soft-delete flag rather than removing rows. Ingest
  pipelines may need to keep historical stocks even after they are
  delisted or no longer tracked.
* ``Numeric`` is used for prices (handled downstream in DailyPrice); here
  the only string fields are the descriptive ones.
* Index on ``is_active`` so active-stock queries are cheap.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from backend.database.models.daily_price import DailyPrice
    from backend.database.models.update_log import UpdateLog


class Stock(Base, TimestampMixin):
    """A tradable instrument tracked by the platform."""

    __tablename__ = "stocks"
    __table_args__ = (
        UniqueConstraint("ticker", "exchange", name="uq_stocks_ticker_exchange"),
        Index("ix_stocks_is_active", "is_active"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    ticker: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    exchange: Mapped[str] = mapped_column(String(50), nullable=False)
    sector: Mapped[str | None] = mapped_column(String(100), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="USD")

    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )

    daily_prices: Mapped[list[DailyPrice]] = relationship(
        back_populates="stock",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    update_logs: Mapped[list[UpdateLog]] = relationship(
        back_populates="stock",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<Stock id={self.id} ticker={self.ticker!r} exchange={self.exchange!r}>"
