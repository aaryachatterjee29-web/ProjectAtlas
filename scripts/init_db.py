"""Initialize the Project Atlas database schema.

Creates every table declared on the SQLAlchemy ``Base.metadata``. This
script is idempotent — existing tables are left untouched.

Configuration
-------------
The target database is controlled by the ``DATABASE_URL`` environment
variable. For local development against SQLite, set::

    DATABASE_URL=sqlite:///./atlas.db

Usage
-----
From the project root, with the virtual environment active::

    python -m scripts.init_db

Or directly::

    python scripts/init_db.py

This script does not insert any data. It only ensures the schema exists.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the project root is on sys.path so `backend.*` imports resolve
# whether the script is run as `python scripts/init_db.py` or as a module.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# Importing the models package registers every model with Base.metadata.
from sqlalchemy import inspect  # noqa: E402

from backend.database import models  # noqa: E402,F401
from backend.database.base import Base  # noqa: E402
from backend.database.engine import get_database_url, get_engine  # noqa: E402


def main() -> None:
    url = get_database_url()
    engine = get_engine()
    print(f"Initializing database at: {url}")

    Base.metadata.create_all(engine)

    inspector = inspect(engine)
    created = sorted(inspector.get_table_names())
    print(f"Tables present after initialization: {created}")

    expected = sorted(Base.metadata.tables.keys())
    missing = [t for t in expected if t not in created]
    if missing:
        raise SystemExit(f"Missing tables after create_all: {missing}")

    print("Database schema initialized successfully.")


if __name__ == "__main__":
    main()
