# SRTP-CAPD Backend MVP

Backend MVP for a CAPD listening rehabilitation mini program. The service exposes a stable `/api/v1` API, stores user training history in SQLite, generates task audio, includes an offline corpus pipeline, and serves a local frontend demo at `/`.

## Quick Start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m compileall -q data_pipeline server tests
pytest -q
python -m uvicorn server.main:app --host 127.0.0.1 --port 8000
```

Open:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/openapi.json`
- `http://127.0.0.1:8000/docs`

The root page is a static demo in `web/`. It can create sessions, request tasks, play returned audio, submit answers, refresh progress, and show API debug/error states.

`GET /api/v1/tasks/next` calls online `edge-tts`. If the current network cannot reach the TTS service, task/audio generation may fail while the rest of the API and frontend remain available for validation.

## Core API

- `GET /health`
- `POST /api/v1/sessions`
- `GET /api/v1/tasks/next?session_id=...`
- `POST /api/v1/answers`
- `GET /api/v1/users/{user_id}/progress`

See `docs/API_CONTRACT.md` for request and response fields.

## Local Smoke Checks

```powershell
python -m compileall -q data_pipeline server tests
pytest -q
python -c "import server.main; print('server import ok')"
```

Run API smoke after starting uvicorn:

```powershell
.\scripts\api_smoke_test.ps1 -BaseUrl http://127.0.0.1:8000 -UserId demo_smoke
```

If online TTS is blocked, this smoke may fail at `/api/v1/tasks/next`. In that case, verify `/`, `/docs`, `/openapi.json`, `/health`, and `POST /api/v1/sessions`, then use the frontend error/debug state as the expected restricted-network behavior.

Run the fast offline pipeline smoke:

```powershell
python -m data_pipeline.run_pipeline --limit 20 --batch-size 8 --resume --scorer heuristic --no-augment --output processed_corpus.txt
```

## Frontend Integration

- Static demo assets live in `web/index.html`, `web/styles.css`, and `web/app.js`.
- Frontend and mini program API guidance lives in `docs/FRONTEND_INTEGRATION.md`.
- `GET /api/v1/tasks/next` uses `edge-tts`; if network access to the TTS service is blocked, the frontend keeps the session visible and shows a retry-friendly task/audio error.

## Demo Guide

Use `docs/DEMO_RUNBOOK.md` for a step-by-step local demo, including the `/` frontend, API responses, database persistence, pipeline output, and generated audio quality.
