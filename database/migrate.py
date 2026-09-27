"""
Lightweight schema migration runner.

`Base.metadata.create_all()` only creates *missing* tables - it never adds
columns to an existing table. This runner applies the SQL files in
`database/migrations/` in filename order, skipping statements whose target
column already exists, so an existing development database can be brought in
line with the ORM models.

Usage:
    python -m database.migrate
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List

from sqlalchemy import inspect, text
from sqlalchemy.exc import OperationalError

from database.connection import Base, engine

MIGRATIONS_DIR = Path(__file__).parent / "migrations"

ADD_COLUMN_RE = re.compile(
    r"^\s*ALTER\s+TABLE\s+(\w+)\s+ADD\s+COLUMN\s+(\w+)",
    re.IGNORECASE,
)


def _existing_columns() -> dict:
    inspector = inspect(engine)
    return {table: {col["name"] for col in inspector.get_columns(table)} for table in inspector.get_table_names()}


def _split_statements(sql: str) -> List[str]:
    return [stmt.strip() for stmt in sql.split(";") if stmt.strip()]


def run_migrations(verbose: bool = True) -> int:
    """Apply pending migrations. Returns the number of statements executed."""
    import src.models  # noqa: F401  (register ORM metadata)

    # New tables first, so migrations can rely on them.
    Base.metadata.create_all(bind=engine)

    applied = 0
    for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
        statements = _split_statements(path.read_text(encoding="utf-8"))
        columns = _existing_columns()
        executed = 0
        for stmt in statements:
            match = ADD_COLUMN_RE.match(stmt)
            if match:
                table, column = match.group(1), match.group(2)
                if table in columns and column in columns[table]:
                    continue
            try:
                with engine.begin() as conn:
                    conn.execute(text(stmt))
                executed += 1
            except OperationalError as exc:
                # Only tolerate the two benign cases:
                #   * "duplicate column name" - a column another migration added
                #   * "no such column"        - an index over a legacy column
                # Everything else is a real failure and must not be hidden.
                message = str(exc.orig).lower()
                if "duplicate column name" in message:
                    continue
                if "no such column" in message and stmt.upper().lstrip().startswith("CREATE INDEX"):
                    if verbose:
                        print(f"      skipped index: {stmt.splitlines()[0][:70]} ({exc.orig})")
                    continue
                raise
        applied += executed
        if verbose:
            status = f"{executed} statement(s) applied" if executed else "already up to date"
            print(f"  - {path.name}: {status}")
    return applied


if __name__ == "__main__":
    print("=" * 60)
    print("AssureX Claim Engine - Applying database migrations")
    print("=" * 60)
    total = run_migrations()
    print(f"Migration run complete ({total} statement(s) applied).")
    sys.exit(0)
