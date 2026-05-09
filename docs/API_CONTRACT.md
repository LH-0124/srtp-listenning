# API_CONTRACT.md - Mini Program Backend API Contract

Base URL:

```text
http://127.0.0.1:8000
```

All new mini program APIs use the `/api/v1` prefix. Legacy `/start`, `/next_task`, and `/submit` endpoints remain for temporary compatibility only.

## 1. GET /health

Purpose: health check for service monitoring.

Response `200`:

```json
{
  "status": "ok",
  "service": "srtp-capd-backend",
  "version": "0.1.0"
}
```

## 2. POST /api/v1/sessions

Purpose: create a persistent training session.

Request:

```json
{
  "user_id": "demo_user",
  "training_mode": "LOW",
  "noise_profile": "none"
}
```

Fields:

- `user_id`: string, required.
- `training_mode`: string, optional, one of `LOW` or `HIGH`, default `LOW`.
- `noise_profile`: string, optional, one of `none`, `white`, `cafe`, `street`, `speech_babble`, default `none`.

Response `200`:

```json
{
  "session_id": "uuid",
  "user_id": "demo_user",
  "training_mode": "LOW",
  "difficulty": {
    "speed": 1.0,
    "snr": 20.0
  }
}
```

## 3. GET /api/v1/tasks/next

Purpose: get the next training task for a session.

Query parameters:

- `session_id`: string, required.

Response `200`:

```json
{
  "task_id": "uuid",
  "session_id": "uuid",
  "text_hash": "sha256",
  "target_text": "demo sentence",
  "audio_url": "http://127.0.0.1:8000/static/task_xxx.wav",
  "difficulty": {
    "speed": 1.0,
    "snr": 20.0,
    "noise_profile": "none"
  }
}
```

Notes:

- `target_text` is returned during MVP development for scoring and debugging.
- `audio_url` is an absolute URL generated from the request host.
- `text_hash` is the SHA-256 hash of `target_text`.
- The selected task is persisted in `training_tasks` before the response returns.
- `noise_profile` is applied during audio generation. Non-`none` profiles are mixed to the requested SNR with deterministic synthetic noise, short fade in/out, RMS normalization, and peak limiting.

Error responses:

- `404`: session not found.
- `503`: no training sentences are available; run the data pipeline first.

## 4. POST /api/v1/answers

Purpose: submit the user's listening or dictation result.

Request:

```json
{
  "session_id": "uuid",
  "task_id": "uuid",
  "user_input": "user answer"
}
```

Response `200`:

```json
{
  "correct": false,
  "score": 0.0,
  "message": "回答错误，难度降低",
  "new_difficulty": {
    "speed": 0.8,
    "snr": 23.0
  }
}
```

Scoring rule for T02 MVP: exact string match after trimming whitespace.

T05 persistence behavior:

- A successful answer submission writes one row to `answers`.
- The related `training_sessions` row stores the new `speed` and `snr`.
- The user's `user_progress` row is updated with cumulative totals, accuracy, and current difficulty.

Error responses:

- `404`: session not found, or task does not belong to the session.

## 5. GET /api/v1/users/{user_id}/progress

Purpose: query user progress summary.

Path parameters:

- `user_id`: string, required.

Response `200`:

```json
{
  "user_id": "demo_user",
  "total_answers": 10,
  "correct_count": 7,
  "accuracy": 0.7,
  "current_difficulty": {
    "speed": 1.2,
    "snr": 16.0
  }
}
```

Progress is read from persistent SQLite user data tables. Unknown users return an initialized zero-progress row with default difficulty.

## Persistent User Data Tables

T05 adds these idempotently with `CREATE TABLE IF NOT EXISTS`; existing `sentences`, `pipeline_runs`, and `pipeline_errors` data are preserved.

- `users`: `id`, `user_id`, `nickname`, `created_at`.
- `training_sessions`: `id`, `session_id`, `user_id`, `training_mode`, `noise_profile`, `speed`, `snr`, `created_at`, `ended_at`.
- `training_tasks`: `id`, `task_id`, `session_id`, `sentence_id`, `target_text`, `audio_url`, `speed`, `snr`, `noise_profile`, `created_at`.
- `answers`: `id`, `answer_id`, `session_id`, `task_id`, `user_input`, `target_text`, `correct`, `score`, `created_at`.
- `user_progress`: `id`, `user_id`, `total_answers`, `correct_count`, `accuracy`, `current_speed`, `current_snr`, `updated_at`.

## 6. GET /openapi.json

Purpose: export OpenAPI JSON for mini program integration and API debugging tools.

FastAPI also serves interactive documentation at:

- `/docs`
- `/redoc`

## Release Smoke Tests

Before handing the API to mini program integration, run:

```powershell
python -m compileall -q data_pipeline server tests
pytest -q
python -c "import server.main; print('server import ok')"
python -m uvicorn server.main:app --host 127.0.0.1 --port 8000
.\scripts\api_smoke_test.ps1 -BaseUrl http://127.0.0.1:8000 -UserId smoke_user
```

The automated tests use a temporary SQLite database and monkeypatch online TTS, so they do not require network access or mutate `capd_database.db`.
