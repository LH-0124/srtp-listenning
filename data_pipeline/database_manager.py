from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "capd_database.db"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def get_connection(db_path: str | os.PathLike[str] | None = None) -> sqlite3.Connection:
    resolved_path = Path(db_path or DB_PATH).resolve()
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(resolved_path)
    conn.row_factory = sqlite3.Row
    return conn


def _table_columns(conn: sqlite3.Connection, table_name: str) -> set[str]:
    rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    return {row["name"] for row in rows}


def init_db(db_path: str | os.PathLike[str] | None = None) -> None:
    """Create and migrate the corpus pipeline tables."""
    with get_connection(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sentences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT UNIQUE,
                context_type TEXT,
                score REAL
            )
            """
        )

        sentence_columns = _table_columns(conn, "sentences")
        if "source" not in sentence_columns:
            conn.execute("ALTER TABLE sentences ADD COLUMN source TEXT DEFAULT 'unknown'")
        if "created_at" not in sentence_columns:
            conn.execute("ALTER TABLE sentences ADD COLUMN created_at TEXT")

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS pipeline_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                input_path TEXT NOT NULL,
                output_path TEXT,
                limit_count INTEGER,
                batch_size INTEGER NOT NULL,
                resume INTEGER NOT NULL DEFAULT 0,
                scorer TEXT NOT NULL,
                augment INTEGER NOT NULL DEFAULT 0,
                processed_count INTEGER NOT NULL DEFAULT 0,
                success_count INTEGER NOT NULL DEFAULT 0,
                failed_count INTEGER NOT NULL DEFAULT 0,
                skipped_count INTEGER NOT NULL DEFAULT 0,
                augmented_count INTEGER NOT NULL DEFAULT 0,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                status TEXT NOT NULL,
                error_message TEXT
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS pipeline_errors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER,
                raw_text TEXT,
                error_message TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(run_id) REFERENCES pipeline_runs(id)
            )
            """
        )

        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_pipeline_errors_run_id
            ON pipeline_errors(run_id)
            """
        )


def create_pipeline_run(
    input_path: str,
    output_path: str,
    limit_count: Optional[int],
    batch_size: int,
    resume: bool,
    scorer: str,
    augment: bool,
    db_path: str | os.PathLike[str] | None = None,
) -> int:
    with get_connection(db_path) as conn:
        cursor = conn.execute(
            """
            INSERT INTO pipeline_runs (
                input_path, output_path, limit_count, batch_size, resume,
                scorer, augment, started_at, status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                input_path,
                output_path,
                limit_count,
                batch_size,
                int(resume),
                scorer,
                int(augment),
                utc_now(),
                "running",
            ),
        )
        return int(cursor.lastrowid)


def update_pipeline_run(
    run_id: int,
    *,
    db_path: str | os.PathLike[str] | None = None,
    **fields: Any,
) -> None:
    if not fields:
        return

    assignments = ", ".join(f"{name} = ?" for name in fields)
    values = list(fields.values())
    values.append(run_id)
    with get_connection(db_path) as conn:
        conn.execute(
            f"UPDATE pipeline_runs SET {assignments} WHERE id = ?",
            values,
        )


def finish_pipeline_run(
    run_id: int,
    status: str,
    *,
    error_message: str | None = None,
    db_path: str | os.PathLike[str] | None = None,
) -> None:
    update_pipeline_run(
        run_id,
        status=status,
        completed_at=utc_now(),
        error_message=error_message,
        db_path=db_path,
    )


def log_pipeline_error(
    run_id: int | None,
    raw_text: str,
    error_message: str,
    db_path: str | os.PathLike[str] | None = None,
) -> None:
    with get_connection(db_path) as conn:
        conn.execute(
            """
            INSERT INTO pipeline_errors (run_id, raw_text, error_message, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (run_id, raw_text, error_message, utc_now()),
        )


def sentence_exists(text: str, db_path: str | os.PathLike[str] | None = None) -> bool:
    with get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT 1 FROM sentences WHERE text = ? LIMIT 1",
            (text,),
        ).fetchone()
        return row is not None


def insert_sentence(
    text: str,
    context_type: str,
    score: float,
    source: str = "pipeline",
    db_path: str | os.PathLike[str] | None = None,
) -> bool:
    with get_connection(db_path) as conn:
        cursor = conn.execute(
            """
            INSERT OR IGNORE INTO sentences (text, context_type, score, source, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (text, context_type, score, source, utc_now()),
        )
        return cursor.rowcount > 0
