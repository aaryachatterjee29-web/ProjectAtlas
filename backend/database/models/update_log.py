"""UpdateLog model.

Audit trail for data ingestion runs. Each row records a single
attempt to refresh a stock's data: when it ran, whether it succeeded,
how many rows were downloaded, and any error message.

Relationships
-------------
* :class:`~backend.database.models.stock.Stock` — each log entry belongs
  to one stock.

Design decisions
----------------
* ``status`` is a constrained ``String`` with allowed values
  ``success``, ``failure``, ``partial``. We avoid a Postgres-native
  ``ENUM`` type so the schema is portable across SQLite (dev) and
  Postgres (prod).
* ``last_updated`` is a ``DateTime`` (with timezone) rather than a
  ``Date`` because update cadence is sub-daily for some workflows.
* ``duration_seconds`` is a ``Float`` — sub-second precision is useful
  for diagnosing slow downloads.
* ``error_message`` is nullable; only set on ``failure`` / ``partial``.
* ``rows_downloaded`` defaults to 0 for failure runs.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base

if TYPE_CHECKING:
    from backend.database.models.stock import Stock


_ALLOWED_STATUSES = ("success", "failure", "partial")


class UpdateLog(Base):
    """One row per data-ingestion attempt for a stock."""

    __tablename__ = "update_logs"
    __table_args__ = (
        CheckConstraint(
            "status IN ('success', 'failure', 'partial')",
            name="ck_update_logs_status",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    stock_id: Mapped[int] = mapped_column(
        ForeignKey("stocks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    last_updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)

    rows_downloaded: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    duration_seconds: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    stock: Mapped[Stock] = relationship(back_populates="update_logs")

    def __repr__(self) -> str:
        return f"<UpdateLog id={self.id} stock_id={self.stock_id} status={self.status!r}>"
