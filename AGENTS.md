# AGENTS.md - SRTP-CAPD Codex Collaboration Rules

## 0. Project Goal

This repository provides the backend MVP for a CAPD listening rehabilitation mini program. The backend should support:

1. selecting training sentences from the corpus database;
2. generating training audio for selected sentences;
3. applying difficulty controls such as speed, SNR, and noise profile;
4. receiving user dictation or recognition answers;
5. recording user sessions, tasks, answers, progress, and difficulty changes;
6. exporting stable API documentation for frontend and mini program integration.

## 1. Required Reading Before Work

Every Codex process must read these files before starting a task:

1. `AGENTS.md`
2. `docs/PROJECT_STATE.md`
3. `docs/STATE_MACHINE.md`
4. `.codex/shared_state.json`
5. the relevant `.codex/tasks/Txx_*.md` task file, when the work is tied to a numbered task.

Do not rely only on the task file. Use `.codex/shared_state.json` and `.codex/logs/` to understand what is complete, blocked, or risky.

## 2. Shared State And Logs

Agents communicate through `.codex/shared_state.json` and `.codex/logs/`.

At task start:

1. set the task status to `in_progress`;
2. set `owner`, for example `codex-T10-full-demo-acceptance`;
3. set `started_at`;
4. avoid changing other task statuses unless a dependency is explicitly completed by your work.

At task completion:

1. set the task status to `done`, `blocked`, or `needs_review`;
2. set `completed_at` or `blocked_reason`;
3. update `files_changed`;
4. update `tests_run`;
5. write a result summary to `.codex/logs/Txx_result.md`;
6. if API behavior changes, update `docs/API_CONTRACT.md` or `docs/openapi-draft.yaml`;
7. if database schema changes, update `docs/DATABASE_SCHEMA.md`.

## 3. Safety Rules

- Do not commit API keys, tokens, cookies, database passwords, cloud credentials, or real user data.
- Do not commit `.env`, `~/.codex/auth.json`, generated audio, virtual environments, caches, or temporary local files.
- Do not delete original corpus data.
- Do not bypass core logic just to make a demo pass.
- Do not rent GPU servers or run full-scale expensive jobs before small smoke tests and timing estimates.
- Do not perform broad refactors unless the user explicitly asks for them.
- Do not modify `Project Completion Defense/` unless the user explicitly asks for that folder.

## 4. Current High-priority Notes

The MVP is now validated through T10. Current practical status:

- `/api/v1` API contract exists and is covered by tests.
- SQLite persistence covers users, sessions, tasks, answers, and progress.
- `GET /` serves the local static frontend demo from `web/`.
- The frontend can create sessions, request tasks, play returned audio when TTS is available, submit answers, refresh progress, and show API debug/error states.
- `GET /api/v1/tasks/next` depends on online `edge-tts`; restricted networks may fail while connecting to `speech.platform.bing.com:443`. This is an environment limitation, not an API contract change.
- `capd_database.db` is a local demo database and may be touched by smoke tests. Do not treat it as production or real user data.

## 5. Recommended Local Commands

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

python -m compileall -q data_pipeline server tests
pytest -q
python -c "import server.main; print('server import ok')"
python -m data_pipeline.run_pipeline --help
```

Start the local API and frontend:

```powershell
python -m uvicorn server.main:app --host 127.0.0.1 --port 8000
```

Open:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/openapi.json`

Run API smoke after the server is running:

```powershell
.\scripts\api_smoke_test.ps1 -BaseUrl http://127.0.0.1:8000 -UserId demo_user
```

If online TTS is blocked, this smoke may fail at `/api/v1/tasks/next`.

## 6. Completion Standard

A task is `done` only when:

1. relevant code compiles;
2. relevant tests or smoke checks have been run, or skipped with a clear reason;
3. API or data-structure changes are documented;
4. `.codex/shared_state.json` is updated;
5. `.codex/logs/Txx_result.md` records what changed, commands run, remaining risks, and submit/no-submit notes.

## 7. Mini Program API Contract

New integration should use the `/api/v1` prefix. Legacy `/start`, `/next_task`, and `/submit` routes are compatibility-only.

Minimum stable endpoints:

- `GET /health`
- `POST /api/v1/sessions`
- `GET /api/v1/tasks/next?session_id=...`
- `POST /api/v1/answers`
- `GET /api/v1/users/{user_id}/progress`
- `GET /openapi.json`

Keep JSON response field names stable unless the user explicitly requests a contract change.
