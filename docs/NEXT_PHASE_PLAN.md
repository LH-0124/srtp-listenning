# Next Phase Plan - Frontend Demo And Integration

Updated: 2026-05-10

## Status

T07, T08, T09, and T10 are complete.

- T07 added the static frontend shell and served it from `/`.
- T08 wired the frontend to the `/api/v1` session/task/audio/answer/progress flow.
- T09 polished the frontend, improved accessibility, responsive layout, theme modes, state handling, and API debug visibility.
- T10 ran final full demo acceptance. Automated tests and static/demo routes passed. Real task/audio/API smoke is limited by online `edge-tts` network access in the current environment.

There is no remaining numbered frontend-demo task in the current plan.

## Current Demo Surface

Start the server:

```powershell
python -m uvicorn server.main:app --host 127.0.0.1 --port 8000
```

Open:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/openapi.json`

The frontend demo can:

- create a session;
- request a next task;
- play returned audio when TTS succeeds;
- submit an answer;
- refresh progress;
- show API request/response debug data;
- show clear loading/error/success/empty states;
- preserve the session when task audio generation fails.

## Known Validation Constraint

`GET /api/v1/tasks/next` depends on online `edge-tts`. In restricted network environments it may fail while connecting to `speech.platform.bing.com:443`.

This does not change the API contract. For local validation, confirm that:

- session creation succeeds;
- task failure is visible and retry-friendly;
- the session remains active after the failure;
- `/`, `/web/app.js`, `/web/styles.css`, `/docs`, and `/openapi.json` return 200.

## T10_full_demo_acceptance

Status: complete.

Acceptance summary:

- `python -m compileall -q data_pipeline server tests` passed.
- `pytest -q` passed.
- `python -c "import server.main; print('server import ok')"` passed.
- `python -m data_pipeline.run_pipeline --help` passed.
- `/`, `/docs`, and `/openapi.json` returned 200 under uvicorn.
- `POST /api/v1/sessions` succeeded.
- `/api/v1/tasks/next` hit the known online TTS/network failure path in this environment.
- API smoke reached health/session and then failed at task generation because online TTS was unavailable.

See `.codex/logs/T10_result.md` for the detailed acceptance record.

## Recommended Checks For Future Changes

```powershell
python -m compileall -q data_pipeline server tests
pytest -q
python -c "import server.main; print('server import ok')"
python -m data_pipeline.run_pipeline --help
```

Start server:

```powershell
python -m uvicorn server.main:app --host 127.0.0.1 --port 8000
```

Check:

- `/`
- `/docs`
- `/openapi.json`
- frontend session creation;
- frontend task success when TTS/network permits;
- frontend task error handling when TTS/network is blocked;
- answer/progress flow where a task exists;
- API smoke script where TTS/network permits.

## Handoff Notes

- Use `docs/DEMO_RUNBOOK.md` for local demo steps.
- Use `docs/FRONTEND_INTEGRATION.md` for mini program integration guidance.
- Keep `/api/v1` response field names stable.
- Do not treat TTS network failure as an API contract change.

## File Hygiene

Do not submit:

- `.env`
- `__pycache__/`
- `.pytest_cache/`
- generated audio under `assets/`
- raw corpus dumps under `data_pipeline/raw_data/`
- real secrets
- real user data
