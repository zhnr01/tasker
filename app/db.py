from collections.abc import Generator

from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlmodel import Session, create_engine

from app.config import get_settings

_engine: Engine | None = None


def check_database() -> bool:
    """Run `SELECT 1` to confirm the DB is reachable. Used by readiness checks."""
    try:
        with Session(get_engine()) as session:
            session.exec(text("SELECT 1"))
        return True
    except Exception:
        return False


def get_engine() -> Engine:
    """Return the process-wide Engine (and its connection pool), lazily built.

    Created on first use so importing this module has no side effects (important
    for tests and tooling). Pool tunables come from config (Part 02).
    """
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_engine(
            str(settings.DATABASE_URL),
            echo=settings.DEBUG,  # log SQL in debug; silent in prod
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            pool_pre_ping=True,  # verify a conn is alive before using it
        )
    return _engine


def get_session() -> Generator[Session]:
    """FastAPI dependency: yield one Session per request, always closed.

    The `with` block guarantees the session (and its borrowed connection) is
    returned to the pool even if the handler raises. Routes never construct their
    own session — they depend on this. (08-layers.md.)
    """
    with Session(get_engine()) as session:
        yield session


def dispose_engine() -> None:
    """Close all pooled connections. Called on shutdown (Part 23)."""
    global _engine
    if _engine is not None:
        _engine.dispose()
        _engine = None
