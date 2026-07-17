"""SQLAlchemy engine factory for Project Atlas.

The engine URL is read from the ``DATABASE_URL`` environment variable. The
factory is lazy: a real engine is only created when ``get_engine()`` is
first called, which keeps imports side-effect free and avoids requiring
``DATABASE_URL`` to be set for unrelated imports (e.g. tests that mock
the engine, or the Alembic offline mode in the future).
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from typing import Any

from sqlalchemy.engine import Engine
from sqlalchemy.engine import create_engine as _sa_create_engine

_engine: Engine | None = None


def get_database_url() -> str:
    """Return the database URL from the environment.

    Raises:
        RuntimeError: if ``DATABASE_URL`` is not set.
    """
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set. Copy .env.example to .env and configure it.")
    return url


def _build_engine(url: str) -> Engine:
    """Build a SQLAlchemy engine appropriate for the given URL.

    SQLite requires ``check_same_thread=False`` when used from a threaded
    context (e.g. FastAPI). For other backends we apply reasonable pooling
    defaults.
    """
    connect_args: dict[str, Any] = {}
    engine_kwargs: dict[str, Any] = {
        "pool_pre_ping": True,
        "future": True,
    }

    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    if not url.startswith("sqlite"):
        engine_kwargs["pool_size"] = 5
        engine_kwargs["max_overflow"] = 10

    engine_kwargs["connect_args"] = connect_args
    return _sa_create_engine(url, **engine_kwargs)


def get_engine() -> Engine:
    """Return the process-wide SQLAlchemy engine, creating it on first use."""
    global _engine
    if _engine is None:
        _engine = _build_engine(get_database_url())
    return _engine


def dispose_engine() -> None:
    """Dispose of the cached engine. Useful for tests and graceful shutdown."""
    global _engine
    if _engine is not None:
        _engine.dispose()
        _engine = None


def engine_healthcheck() -> Iterator[None]:
    """Context manager: yield once the engine can reach the database.

    Currently a placeholder for richer diagnostics; used by health-check
    endpoints in the future.
    """
    with get_engine().connect():
        yield None
