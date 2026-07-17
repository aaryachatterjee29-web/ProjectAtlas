"""Session management for Project Atlas.

This module exposes ``SessionLocal`` (the session factory) and
``get_session`` (a generator suitable for use as a FastAPI dependency).
Sessions are short-lived and must be closed by the caller.

The factory is configured lazily: the engine is bound on first use so
that importing this module does not require ``DATABASE_URL`` to be set.
"""

from __future__ import annotations

from collections.abc import Generator
from typing import TYPE_CHECKING

from sqlalchemy.orm import Session, sessionmaker

from backend.database.engine import get_engine

if TYPE_CHECKING:
    pass


_session_factory: sessionmaker[Session] | None = None


def _get_session_factory() -> sessionmaker[Session]:
    """Return the process-wide session factory, building it on first use."""
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(
            bind=get_engine(),
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
            future=True,
        )
    return _session_factory


def get_session() -> Generator[Session, None, None]:
    """Yield a SQLAlchemy session and ensure it is closed afterwards.

    Intended for use as a FastAPI dependency:

        @app.get("/items")
        def list_items(session: Session = Depends(get_session)):
            ...
    """
    session = _get_session_factory()()
    try:
        yield session
    finally:
        session.close()
