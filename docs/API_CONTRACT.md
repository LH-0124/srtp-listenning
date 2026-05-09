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

Purpose: create an in-memory training session.

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

T02 stores progress in process memory. Persistent user, session, answer, and progress tables are reserved for T05.

## 6. GET /openapi.json

Purpose: export OpenAPI JSON for mini program integration and API debugging tools.

FastAPI also serves interactive documentation at:

- `/docs`
- `/redoc`
