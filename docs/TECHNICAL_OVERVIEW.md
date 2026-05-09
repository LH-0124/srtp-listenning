# SRTP-CAPD MVP Technical Overview

Updated: 2026-05-09

This document summarizes the current backend MVP, local frontend demo, data flow, and validation commands.

## 1. Scope

The repository provides a local MVP for a CAPD listening rehabilitation mini program:

- sentence selection from SQLite corpus data;
- task audio generation with speed, SNR, and noise profile controls;
- user session, task, answer, and progress persistence;
- stable `/api/v1` API contract;
- OpenAPI export and Swagger UI;
- offline corpus processing pipeline;
- local static frontend demo at `/`;
- automated pytest coverage and smoke scripts.

## 2. Directory Map

```text
CAPD_Server_Backend/
├── server/                    # FastAPI online service
│   ├── main.py                # Routes, static frontend mount, API flow
│   ├── models.py              # Pydantic request/response models
│   ├── adaptive_logic.py      # Difficulty adjustment
│   ├── audio_service.py       # TTS, speed, noise mixing, audio saving
│   ├── noise_profiles.py      # Noise profiles, SNR, fade, normalization
│   └── user_data_store.py     # SQLite user/session/task/answer/progress store
├── web/                       # Local frontend demo
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── data_pipeline/             # Offline corpus pipeline
├── tests/                     # pytest suite
├── docs/                      # API, database, pipeline, frontend, demo docs
├── scripts/                   # API smoke scripts
├── assets/                    # Generated audio, ignored by git
├── capd_database.db           # Local demo SQLite database
├── processed_corpus.txt       # Demo pipeline output
├── README.md
├── README-zh.md
└── requirements.txt
```

## 3. Runtime Entrypoints

Start the service:

```powershell
python -m uvicorn server.main:app --host 127.0.0.1 --port 8000
```

Open:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/openapi.json`

Core APIs:

- `POST /api/v1/sessions`
- `GET /api/v1/tasks/next?session_id=...`
- `POST /api/v1/answers`
- `GET /api/v1/users/{user_id}/progress`

Legacy routes `/start`, `/next_task`, and `/submit` remain for compatibility only.

## 4. Training Flow

1. Frontend or mini program creates a session with `POST /api/v1/sessions`.
2. Backend persists the user/session/progress state.
3. Client requests a task with `GET /api/v1/tasks/next`.
4. Backend selects a sentence, generates audio, stores a task, and returns `audio_url`.
5. Client plays the audio and submits dictation to `POST /api/v1/answers`.
6. Backend scores the answer, adjusts difficulty, persists the answer, and updates progress.
7. Client refreshes progress with `GET /api/v1/users/{user_id}/progress`.

The local frontend in `web/app.js` follows this flow and displays request/response debug details.

## 5. Frontend Demo

The `/` page is a static demo served by FastAPI. It includes:

- session setup;
- task/audio panel;
- answer submission panel;
- progress panel;
- API status/debug panel;
- day/night theme;
- loading, error, success, and empty states;
- responsive layout and accessibility affordances.

`target_text` is shown for MVP demonstration/debugging only. A formal training client should hide it until after the answer is submitted.

## 6. Audio Notes

`GET /api/v1/tasks/next` calls `edge-tts`, so it needs network access to Microsoft Edge TTS. In restricted environments this can fail while connecting to `speech.platform.bing.com:443`.

Expected behavior when TTS fails:

- backend may return an error for the task request;
- frontend keeps the current session visible;
- frontend marks task/audio as error and allows retry.

Generated audio files under `assets/` are ignored by git.

## 7. Pipeline Notes

Quick smoke:

```powershell
python -m data_pipeline.run_pipeline --limit 20 --batch-size 8 --resume --scorer heuristic --no-augment --output processed_corpus.txt
```

Use small BERT/LTP samples before considering GPU rental:

```powershell
python -m data_pipeline.run_pipeline --limit 20 --batch-size 8 --resume --scorer bert --no-augment
python -m data_pipeline.run_pipeline --limit 100 --batch-size 8 --resume --scorer bert --no-augment
python -m data_pipeline.run_pipeline --limit 500 --batch-size 8 --resume --scorer bert --no-augment
```

## 8. Validation

```powershell
python -m compileall -q data_pipeline server tests
pytest -q
python -c "import server.main; print('server import ok')"
```

After starting uvicorn:

```powershell
.\scripts\api_smoke_test.ps1 -BaseUrl http://127.0.0.1:8000 -UserId demo_user
```

If online TTS is unavailable, API smoke can fail at task generation. The static routes and frontend error state can still be validated.

## 9. Do Not Commit

- `.env`
- `__pycache__/`
- `*.pyc`
- `.venv/`
- generated audio under `assets/`
- real secrets or real user data
- raw corpus dumps under `data_pipeline/raw_data/`

## 10. Recommended Reading Order

1. `README-zh.md`
2. `docs/DEMO_RUNBOOK.md`
3. `docs/FRONTEND_INTEGRATION.md`
4. `docs/API_CONTRACT.md`
5. `docs/DATABASE_SCHEMA.md`
6. `docs/PIPELINE_RUNBOOK.md`
7. `server/main.py`
8. `web/app.js`
9. `server/user_data_store.py`
10. `server/audio_service.py`
