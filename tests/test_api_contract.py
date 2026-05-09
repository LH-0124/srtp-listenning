import sqlite3


def test_health_and_openapi_core_paths(api_client):
    client, _ = api_client

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json() == {
        "status": "ok",
        "service": "srtp-capd-backend",
        "version": "0.1.0",
    }

    schema = client.get("/openapi.json")
    assert schema.status_code == 200
    paths = schema.json()["paths"]
    for path in [
        "/health",
        "/api/v1/sessions",
        "/api/v1/tasks/next",
        "/api/v1/answers",
        "/api/v1/users/{user_id}/progress",
    ]:
        assert path in paths


def test_root_serves_static_frontend_shell(api_client):
    client, _ = api_client

    root = client.get("/")
    assert root.status_code == 200
    assert "text/html" in root.headers["content-type"]
    assert "CAPD Training Demo" in root.text
    assert "/web/styles.css" in root.text
    assert "/web/app.js" in root.text

    script = client.get("/web/app.js")
    assert script.status_code == 200
    assert "capd-demo-theme" in script.text


def test_session_task_answer_progress_persistence(api_client):
    client, db_path = api_client

    session_resp = client.post(
        "/api/v1/sessions",
        json={
            "user_id": "pytest_user",
            "training_mode": "LOW",
            "noise_profile": "cafe",
        },
    )
    assert session_resp.status_code == 200
    session = session_resp.json()
    assert session["user_id"] == "pytest_user"
    assert session["training_mode"] == "LOW"
    assert session["difficulty"] == {"speed": 1.0, "snr": 20.0}

    progress_before = client.get("/api/v1/users/pytest_user/progress")
    assert progress_before.status_code == 200
    assert progress_before.json()["total_answers"] == 0

    task_resp = client.get(
        "/api/v1/tasks/next",
        params={"session_id": session["session_id"]},
    )
    assert task_resp.status_code == 200
    task = task_resp.json()
    assert task["session_id"] == session["session_id"]
    assert task["target_text"] == "测试句子一"
    assert task["difficulty"]["noise_profile"] == "cafe"
    assert task["audio_url"].endswith("/static/fake_cafe.wav")

    answer_resp = client.post(
        "/api/v1/answers",
        json={
            "session_id": session["session_id"],
            "task_id": task["task_id"],
            "user_input": task["target_text"],
        },
    )
    assert answer_resp.status_code == 200
    answer = answer_resp.json()
    assert answer["correct"] is True
    assert answer["score"] == 1.0
    assert answer["new_difficulty"]["speed"] > 1.0

    progress_after = client.get("/api/v1/users/pytest_user/progress")
    assert progress_after.status_code == 200
    progress = progress_after.json()
    assert progress["total_answers"] == 1
    assert progress["correct_count"] == 1
    assert progress["accuracy"] == 1.0

    with sqlite3.connect(db_path) as conn:
        assert conn.execute("SELECT COUNT(*) FROM training_sessions").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM training_tasks").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM answers").fetchone()[0] == 1
        stored = conn.execute(
            "SELECT user_input, target_text, correct FROM answers"
        ).fetchone()
    assert stored == (task["target_text"], task["target_text"], 1)


def test_invalid_noise_profile_is_rejected(api_client):
    client, _ = api_client

    response = client.post(
        "/api/v1/sessions",
        json={
            "user_id": "bad_profile_user",
            "training_mode": "LOW",
            "noise_profile": "rain",
        },
    )

    assert response.status_code == 422
