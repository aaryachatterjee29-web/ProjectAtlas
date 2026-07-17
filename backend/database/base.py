"""SQLAlchemy declarative base and shared mixins for Project Atlas models.

This module is the foundation of the database layer. It defines:

* ``Base`` — the declarative base class that all ORM models inherit from.
* ``TimestampMixin`` — adds ``created_at`` / ``updated_at`` columns and a
  server-side update trigger for ``updated_at``.

Keeping the base in a single, dependency-free module avoids circular imports
between models and the engine/session modules.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, ClassVar

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Declarative base class for all Project Atlas ORM models.

    Using SQLAlchemy 2.x's typed ``Mapped[...]`` API. All models should
    inherit from this class.
    """

    type_annotation_map: ClassVar[dict[type[Any], Any]] = {}


class TimestampMixin:
    """Adds ``created_at`` and ``updated_at`` columns to a model.

    Both columns are populated by the database (``func.now()``) so timestamps
    are consistent regardless of which application node writes the row.
    ``updated_at`` is refreshed automatically on row update via the
    ``onupdate=func.now()`` directive.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
