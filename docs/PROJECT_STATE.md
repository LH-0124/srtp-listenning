# PROJECT_STATE.md - SRTP-CAPD Project State

Updated: 2026-05-10

## Current Position

The project is now a backend MVP with a local frontend demo. It is suitable for local demonstration and for mini program API integration planning.

Current practical state: `S8_DEMO_READY`.

Practical demo readiness after T07-T10:

- `/api/v1` API contract is implemented and covered by tests.
- SQLite persistence exists for users, sessions, tasks, answers, and progress.
- Offline corpus pipeline supports small smoke runs and resumable processing.
- Audio generation supports configurable noise profiles, fade, normalization, and peak limiting.
- Automated tests pass.
- `GET /` serves a local static frontend demo from `web/`.
- The frontend can drive the session/task/answer/progress API flow and show friendly TTS/network error states.
- T10 full demo acceptance has been run. Automated tests and static/demo routes passed; the real task/audio/API smoke path is limited in this environment by online `edge-tts` network access.

## Completed Milestones

- M0 repository stabilization and secret cleanup.
- M1 stable `/api/v1` API contract.
- M2 user/session/answer/progress persistence.
- M3 pipeline smoke path and runbook.
- M4 audio noise profile improvements.
- M5 tests, API docs, and demo runbook.
- T07 static frontend shell.
- T08 frontend API flow demo.
- T09 frontend polish and accessibility pass.
- T10 full demo acceptance.

## Current Known Risks

- `GET /api/v1/tasks/next` calls online `edge-tts`. In restricted network environments it may fail while connecting to `speech.platform.bing.com:443`. The frontend now preserves the session and shows a clear retry-friendly error.
- Full BERT/LTP/GPT corpus processing has not been benchmarked at large scale. Keep using small smoke runs before considering GPU rental.
- Generated audio naturalness still needs human listening review, especially for noisy profiles.
- `capd_database.db` is a local demo database and may change during smoke tests. Do not treat it as real user data.

## Current Demo Checklist

For local demonstration:

- run `python -m compileall -q data_pipeline server tests`;
- run `pytest -q`;
- start `python -m uvicorn server.main:app --host 127.0.0.1 --port 8000`;
- open `/`, `/docs`, and `/openapi.json`;
- create a session from the frontend;
- request a task if online TTS/network permits;
- if TTS is blocked, confirm the frontend keeps the session and shows task/audio error plus API debug information.

## Next Step

Prepare presentation materials and integration handoff notes. For engineering work, the next useful tasks are:

- confirm online TTS access in the target demo environment;
- perform human listening review of generated audio;
- benchmark larger BERT/LTP/GPT pipeline samples only after small smoke runs are stable;
- keep API field names stable for mini program integration.
