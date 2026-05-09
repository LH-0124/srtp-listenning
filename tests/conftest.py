import sqlite3
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import server.main as main
from data_pipeline.database_manager import init_db as init_pipeline_db
from server.user_data_store import init_user_data_db


@pytest.fixture()
def api_client(tmp_path, monkeypatch):
    db_path = tmp_path / "capd_test.db"
    init_pipeline_db(db_path)
    init_user_data_db(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO sentences (text, context_type, score, source, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("测试句子一", "LOW", 0.3, "pytest", "2026-05-09T00:00:00+00:00"),
        )

    async def fake_generate_task_audio(text, speed, snr, noise_profile="none", seed=None):
        return f"fake_{noise_profile}.wav"

    monkeypatch.setattr(main, "DB_PATH", str(db_path))
    monkeypatch.setattr(main.AudioService, "generate_task_audio", fake_generate_task_audio)
    main.sessions.clear()
    main.tasks.clear()

    return TestClient(main.app), db_path
