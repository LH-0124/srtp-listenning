# Frontend Integration Guide

This guide describes how the local frontend demo and a mini program client should call the SRTP-CAPD MVP backend APIs.

## Base URL

Local development:

```text
http://127.0.0.1:8000
```

All mini program integration should use the `/api/v1` endpoints. The legacy `/start`, `/next_task`, and `/submit` routes are compatibility-only.

## Recommended Flow

1. Create a session with `POST /api/v1/sessions`.
2. Request a task with `GET /api/v1/tasks/next?session_id=...`.
3. Play the returned `audio_url`.
4. Submit the user's dictation with `POST /api/v1/answers`.
5. Refresh progress with `GET /api/v1/users/{user_id}/progress`.

The static demo at `/` follows this same flow in `web/app.js`.

## 1. Create Session

Request:

```http
POST /api/v1/sessions
Content-Type: application/json
```

```json
{
  "user_id": "demo_user",
  "training_mode": "LOW",
  "noise_profile": "none"
}
```

Response:

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

Keep `session_id` on the client for subsequent task and answer calls.

## 2. Get Next Task

Request:

```http
GET /api/v1/tasks/next?session_id=uuid
```

Response:

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

The MVP returns `target_text` so the demo can show and submit predictable answers. Formal training clients should not reveal `target_text` before the user answers; use it only for development, debugging, or post-answer review.

`/api/v1/tasks/next` generates audio through `edge-tts`. If the machine has no network access or TTS fails, the API may return an error instead of `audio_url`. Frontends should show a clear retry/error state and avoid losing the current session.

## 3. Play Audio

Use the returned absolute `audio_url` as the source for the platform audio component.

Browser example:

```html
<audio controls src="http://127.0.0.1:8000/static/task_xxx.wav"></audio>
```

Mini program clients should use the platform's audio API and report load/playback failures separately from API request failures.

## 4. Submit Answer

Request:

```http
POST /api/v1/answers
Content-Type: application/json
```

```json
{
  "session_id": "uuid",
  "task_id": "uuid",
  "user_input": "what the user typed"
}
```

Response:

```json
{
  "correct": false,
  "score": 0.0,
  "message": "feedback text",
  "new_difficulty": {
    "speed": 0.8,
    "snr": 23.0
  }
}
```

After a successful answer submission, refresh progress.

## 5. Query Progress

Request:

```http
GET /api/v1/users/demo_user/progress
```

Response:

```json
{
  "user_id": "demo_user",
  "total_answers": 1,
  "correct_count": 1,
  "accuracy": 1.0,
  "current_difficulty": {
    "speed": 1.2,
    "snr": 16.0
  }
}
```

Unknown users return initialized zero progress.

## Client Error Handling

Handle these states explicitly:

- `404` from task or answer APIs: session or task is stale; create a new session.
- `503` from task API: no usable training sentences exist; run the corpus pipeline.
- TTS/network failure from task API: keep the session visible and allow retry.
- Audio playback failure: show that `audio_url` was returned but could not be loaded by the client.

Do not rename response fields in client adapters unless the adapter preserves the backend contract for downstream screens.
