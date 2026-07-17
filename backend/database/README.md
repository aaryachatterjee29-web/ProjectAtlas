# backend/database

Persistence layer for the platform.

## Structure

```
database/
├── __init__.py
├── base.py        # Declarative Base + TimestampMixin
├── engine.py      # SQLAlchemy engine factory (URL from env, lazy)
├── session.py     # SessionLocal + get_session() FastAPI dependency
├── models/        # ORM model subpackage
│   ├── __init__.py
│   ├── stock.py
│   ├── daily_price.py
│   ├── update_log.py
│   └── README.md
└── README.md
```

## Configuration

The database connection URL is read from the `DATABASE_URL` environment
variable. The engine factory is lazy: the engine is built on first use,
so importing the module does not require `DATABASE_URL` to be set.

## Initialization

Run the schema-creation script:

```bash
python scripts/init_db.py
```

This is idempotent — existing tables are left untouched.

## Design decisions

* **Lazy engine** — `get_engine()` builds the engine on first call.
  Tests, scripts, and offline migrations can import database modules
  without a live connection.
* **Lazy session factory** — `get_session()` builds the sessionmaker on
  first call for the same reason.
* **Soft-delete for stocks** — `Stock.is_active` is the source of truth;
  hard deletion cascades to dependent `DailyPrice` and `UpdateLog` rows.
* **Portable constraints** — `UpdateLog.status` uses a `CheckConstraint`
  on a `String`, not a native `ENUM`, so the schema works on SQLite and
  Postgres identically.
