# T06 Tests Docs Release Result

Completed at: 2026-05-09T18:25:00+08:00
Owner: codex-T06-tests-docs-release

## Summary

Added automated release coverage and demo handoff docs for the backend MVP without changing the stable T02/T05 API fields.

## Tests Added

- `tests/test_api_contract.py`: covers `GET /health`, OpenAPI core paths, `POST /api/v1/sessions`, `GET /api/v1/tasks/next`, `POST /api/v1/answers`, progress persistence, and invalid `noise_profile` validation.
- `tests/test_database_schema.py`: verifies combined pipeline and user-data SQLite tables.
- `tests/test_pipeline_smoke.py`: covers `run_pipeline --help` parsing and a heuristic pipeline run against temporary input/output/database files.
- `tests/test_audio_noise_profiles.py`: covers `none`, `white`, `cafe`, `street`, `speech_babble`, fixed-seed reproducibility, non-silence, peak limiting, and invalid profile errors.
- `tests/conftest.py`: creates a temporary SQLite database and monkeypatches TTS audio generation so tests do not mutate `capd_database.db` or require network access.

## Docs And Scripts Added

- Added `README.md` with local setup, test, API, and smoke commands.
- Added `docs/DATABASE_SCHEMA.md`.
- Added `docs/DEMO_RUNBOOK.md`.
- Added `.codex/FUNCTIONAL_TEST_PLAN.md`.
- Added `scripts/api_smoke_test.ps1` and `scripts/api_smoke_test.sh`.
- Updated `docs/API_CONTRACT.md` with release smoke commands.
- Added `pytest` to `requirements.txt`.

## Validation

Passed:

- `python -m pip install -r requirements.txt`
- `python -m compileall -q data_pipeline server tests`
- `pytest -q` -> `13 passed`
- `python -m data_pipeline.run_pipeline --help`
- `python -c "import server.main; print('server import ok')"`

Notes:

- `pytest -q` initially failed because pytest was not installed; `requirements.txt` now includes it and installing requirements resolved the issue.
- The shell prints PowerShell profile and xonsh history permission warnings after commands, but the relevant validation commands returned exit code 0.

## Remaining Risks

- Real online `edge_tts` generation is not exercised by pytest; tests intentionally monkeypatch it to avoid network dependency.
- Noise profile naturalness still needs a human listening pass using `docs/DEMO_RUNBOOK.md`.
- Full BERT/LTP/GPT pipeline runs are still outside the fast T06 smoke path; only the heuristic pipeline path is automated.
