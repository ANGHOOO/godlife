"""Session factory and FastAPI-friendly session dependency helpers."""

from __future__ import annotations

import os
from collections.abc import Generator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker


def _database_url() -> str:
    return os.getenv("DATABASE_URL", "sqlite:///./godlife_backend.db")


_ENGINES: dict[str, Engine] = {}
_SESSION_FACTORIES: dict[str, sessionmaker[Session]] = {}


def _engine() -> Engine:
    if "default" not in _ENGINES:
        _ENGINES["default"] = create_engine(
            _database_url(),
            future=True,
            echo=os.getenv("GODLIFE_DB_ECHO", "false").lower() in {"1", "true", "yes"},
        )
    return _ENGINES["default"]


def _session_factory() -> sessionmaker[Session]:
    if "default" not in _SESSION_FACTORIES:
        _SESSION_FACTORIES["default"] = sessionmaker(
            bind=_engine(),
            class_=Session,
            expire_on_commit=False,
            autoflush=False,
        )
    return _SESSION_FACTORIES["default"]


def get_session() -> Generator[Session]:
    """Yield SQLAlchemy session for FastAPI dependencies."""

    session = _session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
