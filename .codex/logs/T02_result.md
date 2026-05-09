# T02_api_contract Result

Completed at: 2026-05-09T16:13:33+08:00
Owner: codex-T02-api

## Summary

Implemented the MVP API contract for mini program integration:

- Added `GET /health`.
- Added `POST /api/v1/sessions`.
- Added `GET /api/v1/tasks/next?session_id=...`.
- Added `POST /api/v1/answers`.
- Added `GET /api/v1/users/{user_id}/progress`.
- Kept legacy `/start`, `/next_task`, and `/submit` routes for temporary compatibility.
- Added stable Pydantic request and response models.
- Updated `docs/API_CONTRACT.md`.
- Updated `docs/openapi-draft.yaml`.

## Files Changed

- `server/main.py`
- `server/models.py`
- `docs/API_CONTRACT.md`
- `docs/openapi-draft.yaml`
- `.codex/shared_state.json`
- `.codex/logs/T02_result.md`

## Validation

- `python -m compileall -q server` - passed.
- `python -c "from server.main import app; schema=app.openapi(); print(schema['info']['title']); print('/api/v1/sessions' in schema['paths']); print('/health' in schema['paths'])"` - passed.

## Remaining Risks

- T02 progress and task records are in memory only. Persistent users, sessions, answers, and progress remain in T05 scope.
- `/api/v1/tasks/next` still depends on existing `sentences` data and online TTS generation. If the database is empty or TTS/network fails, the endpoint cannot produce a usable task.
- Noise profile is accepted and returned by the API contract, but audio generation still uses the current white-noise implementation. Profile-specific noise generation remains in T04 scope.
