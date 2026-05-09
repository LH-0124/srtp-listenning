# Next Phase Plan - Frontend Demo And Integration

Updated: 2026-05-09

## Status

T07, T08, and T09 are complete.

- T07 added the static frontend shell and served it from `/`.
- T08 wired the frontend to the `/api/v1` session/task/audio/answer/progress flow.
- T09 polished the frontend, improved accessibility, responsive layout, theme modes, state handling, and API debug visibility.

The remaining next-phase task is T10 full demo acceptance.

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

Goal: final acceptance for backend plus local frontend demo.

Required reads:

- `AGENTS.md`
- `.codex/shared_state.json`
- `docs/API_CONTRACT.md`
- `docs/TECHNICAL_OVERVIEW.md`
- `docs/NEXT_PHASE_PLAN.md`
- `docs/FRONTEND_INTEGRATION.md`
- `.codex/logs/T07_result.md`
- `.codex/logs/T08_result.md`
- `.codex/logs/T09_result.md`
- `.codex/tasks/T10_full_demo_acceptance.md`

Recommended checks:

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

Outputs:

- update `.codex/shared_state.json`;
- write `.codex/logs/T10_result.md`;
- update README/demo docs only if final acceptance finds gaps;
- produce a final submit/no-submit file list.

## File Hygiene

Do not submit:

- `.env`
- `__pycache__/`
- `.pytest_cache/`
- generated audio under `assets/`
- raw corpus dumps under `data_pipeline/raw_data/`
- real secrets
- real user data
