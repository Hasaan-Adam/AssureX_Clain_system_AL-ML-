"""
AssureX Claim Engine - Database Initialization Script
Creates all tables defined in SQLAlchemy ORM models metadata.
"""

import sys
from database.connection import Base, engine
import src.models  # Import all models to register them on Base.metadata


def init_db() -> None:
    """Create all database tables."""
    print("=" * 60)
    print("AssureX Claim Engine - Initializing Database Schema...")
    print(f"Target Database URL: {engine.url}")
    print("=" * 60)

    try:
        Base.metadata.create_all(bind=engine)
        table_names = list(Base.metadata.tables.keys())
        print(f" Successfully created {len(table_names)} tables:")
        for table in sorted(table_names):
            print(f"  - {table}")
        print("=" * 60)
        print("Database schema initialized successfully.")
    except Exception as exc:
        print(f" Failed to initialize database schema: {exc}", file=sys.stderr)
        raise exc


if __name__ == "__main__":
    init_db()