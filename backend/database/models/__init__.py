"""ORM models for Project Atlas.

This subpackage contains the SQLAlchemy 2.x typed models that define the
platform's persistent schema. Models are imported here for convenient
``Base.metadata`` discovery — importing ``backend.database.models`` (or any
submodule) registers all tables with the shared ``Base``.
"""

from __future__ import annotations

from backend.database.models.daily_price import DailyPrice
from backend.database.models.stock import Stock
from backend.database.models.update_log import UpdateLog

__all__ = ["DailyPrice", "Stock", "UpdateLog"]
