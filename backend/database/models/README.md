# backend/database/models

ORM model definitions for Project Atlas.

This subpackage contains the SQLAlchemy 2.x typed models that define the
platform's persistent schema. Each model lives in its own module and is
re-exported from this package for convenient ``Base.metadata`` discovery
— importing ``backend.database.models`` (or any submodule) registers all
tables with the shared ``Base`.

## Models

* **`stock.py`** — `Stock` — a tradable instrument (e.g. an equity).
  Unique on `(ticker, exchange)`. Soft-delete via `is_active`.
* **`daily_price.py`** — `DailyPrice` — OHLCV + corporate actions for one
  stock on one trading day. Unique on `(stock_id, date)`. Uses
  `Numeric(20, 8)` for monetary fields to avoid floating-point drift.
* **`update_log.py`** — `UpdateLog` — one row per data-ingestion attempt
  for a stock. Captures status (`success` / `failure` / `partial`),
  rows downloaded, duration, and any error message.

## Relationships

```
Stock 1 ──< DailyPrice
Stock 1 ──< UpdateLog
```

Both child tables cascade-delete when the parent `Stock` is removed.

## Adding a new model

1. Create `backend/database/models/<name>.py` defining the class
   inheriting from `Base` (and `TimestampMixin` if you need
   `created_at` / `updated_at`).
2. Re-export it from `backend/database/models/__init__.py`.
3. Run `python scripts/init_db.py` to create the new table.

## Design decisions

* **Type-first ORM** — every column is declared with `Mapped[...]`,
  giving static type information to MyPy and IDE tooling.
* **Soft-delete for stocks, hard-delete for prices and logs** — historical
  price data is removed when a stock is removed (cascade), but stocks
  themselves are kept via `is_active`.
* **Portable constraints** — `UpdateLog.status` uses a `CheckConstraint`
  on a `String` column rather than a native `ENUM`, so the schema works
  on both SQLite (development) and Postgres (production).
