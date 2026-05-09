# T05 User Data Result

Completed at: 2026-05-09T17:05:00+08:00
Owner: codex-T05-user-data

## Summary

Implemented persistent user training data for the API layer while preserving the T02 response fields.

Changes:

- Added `server/user_data_store.py` with idempotent SQLite initialization and CRUD helpers.
- Created persistent `users`, `training_sessions`, `training_tasks`, `answers`, and `user_progress` tables.
- `POST /api/v1/sessions` now creates a persisted user, session, and zero-progress row.
- `GET /api/v1/tasks/next` now persists the selected task after audio generation.
- `POST /api/v1/answers` now writes an `answers` row, updates session difficulty, and updates `user_progress`.
- `GET /api/v1/users/{user_id}/progress` now returns persisted cumulative statistics.
- Legacy `/start`, `/next_task`, and `/submit` remain available; legacy submit creates a compatibility task record so the answer still persists.
- Updated `docs/API_CONTRACT.md` and `docs/openapi-draft.yaml`.

## Database Tables Added

- `users`: `id`, `user_id`, `nickname`, `created_at`
- `training_sessions`: `id`, `session_id`, `user_id`, `training_mode`, `noise_profile`, `speed`, `snr`, `created_at`, `ended_at`
- `training_tasks`: `id`, `task_id`, `session_id`, `sentence_id`, `target_text`, `audio_url`, `speed`, `snr`, `noise_profile`, `created_at`
- `answers`: `id`, `answer_id`, `session_id`, `task_id`, `user_input`, `target_text`, `correct`, `score`, `created_at`
- `user_progress`: `id`, `user_id`, `total_answers`, `correct_count`, `accuracy`, `current_speed`, `current_snr`, `updated_at`

The migration uses `CREATE TABLE IF NOT EXISTS` and indexes only; it does not modify or delete existing `sentences`, `pipeline_runs`, or `pipeline_errors` data.

## Validation

Passed:

- `python -m compileall -q data_pipeline server`
- `python -c "import server.main; print('server import ok')"`
- `python -c "from fastapi.testclient import TestClient; from server.main import app; c=TestClient(app); s=c.post('/api/v1/sessions', json={'user_id':'demo_user_t05','training_mode':'LOW','noise_profile':'none'}); print('session', s.status_code, s.json()); p=c.get('/api/v1/users/demo_user_t05/progress'); print('progress_before', p.status_code, p.json())"`
- Offline answer smoke without online TTS: created a session, inserted a `training_tasks` row directly through the data store, submitted via `POST /api/v1/answers`, verified one `answers` row, updated progress, and updated session difficulty.
- SQLite schema inspection confirmed `answers`, `training_sessions`, `training_tasks`, `user_progress`, and `users` exist alongside existing pipeline tables.

## Remaining Risks

- T04 still owns natural noise profile generation, fade in/out, RMS normalization, and audio-quality validation.
- T06 should add automated tests around persistence, duplicate/invalid task behavior, and OpenAPI contract checks.
- The current scoring rule is still the T02 exact trimmed string match; richer speech/dictation scoring is outside T05.
