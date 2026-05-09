# SRTP-CAPD Backend MVP

Backend MVP for a CAPD listening rehabilitation mini program. The service exposes a stable `/api/v1` API, stores user training history in SQLite, generates task audio, and includes an offline corpus pipeline.

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

OpenAPI is available at:

- `http://127.0.0.1:8000/openapi.json`
- `http://127.0.0.1:8000/docs`

## Core API

- `GET /health`
- `POST /api/v1/sessions`
- `GET /api/v1/tasks/next?session_id=...`
- `POST /api/v1/answers`
- `GET /api/v1/users/{user_id}/progress`

See `docs/API_CONTRACT.md` for request and response fields.

## Local Smoke Checks

Run tests:

```powershell
python -m compileall -q data_pipeline server tests
pytest -q
python -c "import server.main; print('server import ok')"
```

Run API smoke after starting uvicorn:

```powershell
.\scripts\api_smoke_test.ps1 -BaseUrl http://127.0.0.1:8000 -UserId demo_smoke
```

Run the fast offline pipeline smoke:

```powershell
python -m data_pipeline.run_pipeline --limit 20 --batch-size 8 --resume --scorer heuristic --no-augment --output processed_corpus.txt
```

## Demo Guide

Use `docs/DEMO_RUNBOOK.md` for a step-by-step local demo, including how to inspect API responses, database persistence, pipeline output, and generated audio quality.
