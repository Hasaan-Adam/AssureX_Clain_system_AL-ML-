"""Database Connection & Engine Management

Supports SQLite (dev) and PostgreSQL (prod) with connection pooling.
"""

from __future__ import annotations

from typing import Any, Dict

from sqlalchemy import create_engine, event, Engine
from sqlalchemy.orm import sessionmaker, declarative_base

from src.config import settings

# Base Declarative Model
Base = declarative_base()


def get_engine_args(database_url: str) -> Dict[str, Any]:
    """Configure database engine connection arguments based on backend type."""
    engine_kwargs: Dict[str, Any] = {
        "echo": settings.database.echo,
    }

    if database_url.startswith("sqlite"):
        engine_kwargs["connect_args"] = {"check_same_thread": False}
    else:
        # PostgreSQL / MySQL pooling options
        engine_kwargs["pool_pre_ping"] = settings.database.pool_pre_ping
        engine_kwargs["pool_size"] = getattr(settings.database, "pool_size", 10)
        engine_kwargs["max_overflow"] = getattr(settings.database, "max_overflow", 20)

    return engine_kwargs


# Enable foreign key constraints for SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    # Check if the connection is for SQLite
    try:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    except Exception:
        pass  # Ignore if not SQLite or already set


# Database URL from settings
DATABASE_URL = settings.database.url

# Instantiate Engine
engine = create_engine(DATABASE_URL, **get_engine_args(DATABASE_URL))

# Session Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base Declarative Model (imported by models)
Base = declarative_base()


def get_db():
    """FastAPI dependency providing a SQLAlchemy session."""
    from sqlalchemy.orm import Session
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables in the database."""
    # Import all models to register them with Base
    from database.models import Base
    Base.metadata.create_all(bind=engine)


def drop_db():
    """Drop all tables (use with caution)."""
    Base.metadata.drop_all(bind=engine)