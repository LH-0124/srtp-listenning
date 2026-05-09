import sqlite3

from data_pipeline.database_manager import init_db
from server.user_data_store import init_user_data_db


def test_combined_database_schema_has_pipeline_and_user_tables(tmp_path):
    db_path = tmp_path / "schema.db"
    init_db(db_path)
    init_user_data_db(db_path)

    with sqlite3.connect(db_path) as conn:
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }
        session_columns = {
            row[1] for row in conn.execute("PRAGMA table_info(training_sessions)")
        }
        sentence_columns = {
            row[1] for row in conn.execute("PRAGMA table_info(sentences)")
        }

    assert {
        "sentences",
        "pipeline_runs",
        "pipeline_errors",
        "users",
        "training_sessions",
        "training_tasks",
        "answers",
        "user_progress",
    }.issubset(tables)
    assert {"session_id", "user_id", "noise_profile", "speed", "snr"}.issubset(
        session_columns
    )
    assert {"text", "context_type", "score", "source", "created_at"}.issubset(
        sentence_columns
    )
