# PROJECT_STATE.md - SRTP-CAPD Project State

Updated: 2026-05-09

## Current Position

The project is now a backend MVP with a local frontend demo. It is suitable for local demonstration and for mini program API integration planning.

Current state in `.codex/shared_state.json`: `S6_TESTS_READY`.

Practical demo readiness after T07-T09:

- `/api/v1` API contract is implemented and covered by tests.
- SQLite persistence exists for users, sessions, tasks, answers, and progress.
- Offline corpus pipeline supports small smoke runs and resumable processing.
- Audio generation supports configurable noise profiles, fade, normalization, and peak limiting.
- Automated tests pass.
- `GET /` serves a local static frontend demo from `web/`.
- The frontend can drive the session/task/answer/progress API flow and show friendly TTS/network error states.

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

## Current Known Risks

- `GET /api/v1/tasks/next` calls online `edge-tts`. In restricted network environments it may fail while connecting to `speech.platform.bing.com:443`. The frontend now preserves the session and shows a clear retry-friendly error.
- Full BERT/LTP/GPT corpus processing has not been benchmarked at large scale. Keep using small smoke runs before considering GPU rental.
- Generated audio naturalness still needs human listening review, especially for noisy profiles.
- `capd_database.db` is a local demo database and may change during smoke tests. Do not treat it as real user data.

## Next Step

Run T10 full demo acceptance:

- rerun automated tests;
- verify `/`, `/docs`, and `/openapi.json`;
- run API smoke where TTS/network permits;
- update final README/demo docs if needed;
- produce the final submit/no-submit file list.
