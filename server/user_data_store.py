from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "capd_database.db"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def get_connection(db_path: str | os.PathLike[str] | None = None) -> sqlite3.Connection:
    resolved_path = Path(db_path or DB_PATH).resolve()
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(resolved_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_user_data_db(db_path: str | os.PathLike[str] | None = None) -> None:
    """Create persistent user training tables without touching corpus tables."""
    with get_connection(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL UNIQUE,
                nickname TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS training_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL UNIQUE,
                user_id TEXT NOT NULL,
                training_mode TEXT NOT NULL,
                noise_profile TEXT NOT NULL DEFAULT 'none',
                speed REAL NOT NULL,
                snr REAL NOT NULL,
                created_at TEXT NOT NULL,
                ended_at TEXT,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS training_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL UNIQUE,
                session_id TEXT NOT NULL,
                sentence_id INTEGER,
                target_text TEXT NOT NULL,
                audio_url TEXT,
                speed REAL NOT NULL,
                snr REAL NOT NULL,
                noise_profile TEXT NOT NULL DEFAULT 'none',
                created_at TEXT NOT NULL,
                FOREIGN KEY(session_id) REFERENCES training_sessions(session_id),
                FOREIGN KEY(sentence_id) REFERENCES sentences(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                answer_id TEXT NOT NULL UNIQUE,
                session_id TEXT NOT NULL,
                task_id TEXT NOT NULL,
                user_input TEXT NOT NULL,
                target_text TEXT NOT NULL,
                correct INTEGER NOT NULL,
                score REAL NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(session_id) REFERENCES training_sessions(session_id),
                FOREIGN KEY(task_id) REFERENCES training_tasks(task_id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL UNIQUE,
                total_answers INTEGER NOT NULL DEFAULT 0,
                correct_count INTEGER NOT NULL DEFAULT 0,
                accuracy REAL NOT NULL DEFAULT 0.0,
                current_speed REAL NOT NULL DEFAULT 1.0,
                current_snr REAL NOT NULL DEFAULT 20.0,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_training_sessions_user_id
            ON training_sessions(user_id)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_training_tasks_session_id
            ON training_tasks(session_id)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_answers_session_id
            ON answers(session_id)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_answers_task_id
            ON answers(task_id)
            """
        )


def ensure_user(user_id: str, db_path: str | os.PathLike[str] | None = None) -> None:
    now = utc_now()
    with get_connection(db_path) as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO users (user_id, created_at)
            VALUES (?, ?)
            """,
            (user_id, now),
        )
        conn.execute(
            """
            INSERT OR IGNORE INTO user_progress (
                user_id, total_answers, correct_count, accuracy,
                current_speed, current_snr, updated_at
            )
            VALUES (?, 0, 0, 0.0, 1.0, 20.0, ?)
            """,
            (user_id, now),
        )


def create_training_session(
    *,
    session_id: str,
    user_id: str,
    training_mode: str,
    noise_profile: str,
    speed: float,
    snr: float,
    db_path: str | os.PathLike[str] | None = None,
) -> None:
    ensure_user(user_id, db_path)
    with get_connection(db_path) as conn:
        conn.execute(
            """
            INSERT INTO training_sessions (
                session_id, user_id, training_mode, noise_profile,
                speed, snr, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (session_id, user_id, training_mode, noise_profile, speed, snr, utc_now()),
        )


def get_training_session(
    session_id: str,
    db_path: str | os.PathLike[str] | None = None,
) -> dict[str, Any] | None:
    with get_connection(db_path) as conn:
        row = conn.execute(
            """
            SELECT session_id, user_id, training_mode, noise_profile, speed, snr
            FROM training_sessions
            WHERE session_id = ?
            """,
            (session_id,),
        ).fetchone()
    return dict(row) if row else None


def get_latest_session_for_user(
    user_id: str,
    db_path: str | os.PathLike[str] | None = None,
) -> dict[str, Any] | None:
    with get_connection(db_path) as conn:
        row = conn.execute(
            """
            SELECT session_id, user_id, training_mode, noise_profile, speed, snr
            FROM training_sessions
            WHERE user_id = ? AND ended_at IS NULL
            ORDER BY id DESC
            LIMIT 1
            """,
            (user_id,),
        ).fetchone()
    return dict(row) if row else None


def update_session_difficulty(
    session_id: str,
    speed: float,
    snr: float,
    db_path: str | os.PathLike[str] | None = None,
) -> None:
    with get_connection(db_path) as conn:
        conn.execute(
            """
            UPDATE training_sessions
            SET speed = ?, snr = ?
            WHERE session_id = ?
            """,
            (speed, snr, session_id),
        )


def select_sentence(
    training_mode: str,
    db_path: str | os.PathLike[str] | None = None,
) -> dict[str, Any] | None:
    with get_connection(db_path) as conn:
        row = conn.execute(
            """
            SELECT id, text
            FROM sentences
            WHERE context_type = ?
            ORDER BY RANDOM()
            LIMIT 1
            """,
            (training_mode,),
        ).fetchone()
        if row is None:
            row = conn.execute(
                """
                SELECT id, text
                FROM sentences
                ORDER BY RANDOM()
                LIMIT 1
                """
            ).fetchone()
    return dict(row) if row else None


def create_training_task(
    *,
    task_id: str,
    session_id: str,
    sentence_id: int | None,
    target_text: str,
    audio_url: str | None,
    speed: float,
    snr: float,
    noise_profile: str,
    db_path: str | os.PathLike[str] | None = None,
) -> None:
    with get_connection(db_path) as conn:
        conn.execute(
            """
            INSERT INTO training_tasks (
                task_id, session_id, sentence_id, target_text, audio_url,
                speed, snr, noise_profile, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                task_id,
                session_id,
                sentence_id,
                target_text,
                audio_url,
                speed,
                snr,
                noise_profile,
                utc_now(),
            ),
        )


def get_training_task(
    task_id: str,
    db_path: str | os.PathLike[str] | None = None,
) -> dict[str, Any] | None:
    with get_connection(db_path) as conn:
        row = conn.execute(
            """
            SELECT task_id, session_id, sentence_id, target_text, audio_url,
                   speed, snr, noise_profile
            FROM training_tasks
            WHERE task_id = ?
            """,
            (task_id,),
        ).fetchone()
    return dict(row) if row else None


def record_answer(
    *,
    answer_id: str,
    session_id: str,
    task_id: str,
    user_id: str,
    user_input: str,
    target_text: str,
    correct: bool,
    score: float,
    current_speed: float,
    current_snr: float,
    db_path: str | os.PathLike[str] | None = None,
) -> None:
    now = utc_now()
    with get_connection(db_path) as conn:
        conn.execute(
            """
            INSERT INTO answers (
                answer_id, session_id, task_id, user_input, target_text,
                correct, score, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                answer_id,
                session_id,
                task_id,
                user_input,
                target_text,
                int(correct),
                score,
                now,
            ),
        )
        row = conn.execute(
            """
            SELECT total_answers, correct_count
            FROM user_progress
            WHERE user_id = ?
            """,
            (user_id,),
        ).fetchone()
        if row is None:
            total_answers = 1
            correct_count = 1 if correct else 0
            accuracy = correct_count / total_answers
            conn.execute(
                """
                INSERT INTO user_progress (
                    user_id, total_answers, correct_count, accuracy,
                    current_speed, current_snr, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    total_answers,
                    correct_count,
                    accuracy,
                    current_speed,
                    current_snr,
                    now,
                ),
            )
        else:
            total_answers = int(row["total_answers"]) + 1
            correct_count = int(row["correct_count"]) + (1 if correct else 0)
            accuracy = correct_count / total_answers
            conn.execute(
                """
                UPDATE user_progress
                SET total_answers = ?,
                    correct_count = ?,
                    accuracy = ?,
                    current_speed = ?,
                    current_snr = ?,
                    updated_at = ?
                WHERE user_id = ?
                """,
                (
                    total_answers,
                    correct_count,
                    accuracy,
                    current_speed,
                    current_snr,
                    now,
                    user_id,
                ),
            )


def get_user_progress(
    user_id: str,
    db_path: str | os.PathLike[str] | None = None,
) -> dict[str, Any]:
    ensure_user(user_id, db_path)
    with get_connection(db_path) as conn:
        row = conn.execute(
            """
            SELECT user_id, total_answers, correct_count, accuracy,
                   current_speed, current_snr
            FROM user_progress
            WHERE user_id = ?
            """,
            (user_id,),
        ).fetchone()
    return dict(row)
