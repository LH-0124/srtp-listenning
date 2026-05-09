# Database Schema

The MVP uses SQLite at `capd_database.db` by default. Tests use temporary SQLite files and should not modify the project database.

## Corpus And Pipeline Tables

- `sentences`: training corpus rows with `text`, `context_type`, `score`, `source`, and `created_at`.
- `pipeline_runs`: one row per offline pipeline execution with input/output paths, batch settings, scorer, counters, timestamps, status, and error message.
- `pipeline_errors`: per-sentence pipeline failures with `run_id`, raw text, error message, and timestamp.

## User Training Tables

- `users`: stable `user_id`, optional nickname, and creation time.
- `training_sessions`: session id, user id, training mode, noise profile, current speed, current SNR, creation time, and optional end time.
- `training_tasks`: task id, session id, optional sentence id, target text, audio URL, speed, SNR, noise profile, and creation time.
- `answers`: answer id, session id, task id, user input, target text, correctness, score, and creation time.
- `user_progress`: cumulative answer count, correct count, accuracy, current speed, current SNR, and update time.

All schema creation is idempotent via `CREATE TABLE IF NOT EXISTS`. Pipeline migrations preserve existing `sentences` content.
